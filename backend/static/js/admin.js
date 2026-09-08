document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const togglePasswordBtn = document.querySelector('.toggle-password');

  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', () => {
      const type = passwordInput.type === 'password' ? 'text' : 'password';
      passwordInput.type = type;
      togglePasswordBtn.textContent = type === 'password' ? 'Show' : 'Hide';
    });
  }

  const imageUpload = document.getElementById('imageUpload');
  const previewGrid = document.getElementById('previewGrid');
  if (imageUpload && previewGrid) {
    imageUpload.addEventListener('change', (event) => {
      const files = Array.from(event.target.files || []);
      previewGrid.innerHTML = '';
      files.forEach((file) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        const url = URL.createObjectURL(file);
        item.innerHTML = `
          <img src="${url}" alt="${file.name}" />
          <button type="button" data-remove-file="${file.name}">×</button>
        `;
        item.querySelector('button').addEventListener('click', () => {
          item.remove();
        });
        previewGrid.appendChild(item);
      });
    });
  }

  const projectForm = document.getElementById('projectForm');
  if (projectForm) {
    projectForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(projectForm);
      fetch('/admin/api/projects', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
      })
        .then(async (response) => {
          const payload = await response.json().catch(() => ({}));
          if (!response.ok) {
            throw new Error(payload.error || 'Unable to save project.');
          }
          window.location.href = payload.redirect || '/admin/projects';
        })
        .catch((error) => {
          alert(error.message || 'Something went wrong.');
        });
    });
  }

  const settingsForm = document.getElementById('settingsForm');
  if (settingsForm) {
    settingsForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const payload = {};
      new FormData(settingsForm).forEach((value, key) => {
        payload[key] = value;
      });
      fetch('/admin/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'same-origin'
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.reload();
          } else {
            alert(data.error || 'Unable to save settings.');
          }
        })
        .catch(() => alert('Unable to save settings.'));
    });
  }

  const deleteButtons = document.querySelectorAll('[data-delete-project]');
  deleteButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const id = button.dataset.deleteProject;
      if (!window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
        return;
      }
      fetch(`/admin/api/projects/${id}`, {
        method: 'DELETE',
        credentials: 'same-origin'
      })
        .then(async (response) => {
          const payload = await response.json().catch(() => ({}));
          if (!response.ok) {
            throw new Error(payload.error || 'Unable to delete project.');
          }
          window.location.reload();
        })
        .catch((error) => alert(error.message || 'Delete failed.'));
    });
  });

  const editForm = document.querySelector('[data-edit-form="true"]');
  if (editForm) {
    editForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(editForm);
      const action = editForm.getAttribute('action');
      fetch(action, {
        method: 'PUT',
        body: formData,
        credentials: 'same-origin'
      })
        .then(async (response) => {
          const payload = await response.json().catch(() => ({}));
          if (!response.ok) {
            throw new Error(payload.error || 'Unable to update project.');
          }
          window.location.href = '/admin/projects';
        })
        .catch((error) => alert(error.message || 'Update failed.'));
    });
  }
});
