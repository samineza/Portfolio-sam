const portfolioItems = [
  {
    title: "Cultural Pulse",
    category: "Photography",
    image: "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1200&q=80",
    client: "Kigali Cultural Hub",
    software: "Adobe Lightroom, Photoshop",
    description: "A portrait-driven visual campaign capturing the energy, rhythm, and authentic character of a community arts initiative in Kigali."
  },
  {
    title: "Brand Story Reel",
    category: "Video",
    image: "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=1200&q=80",
    client: "Amani Studio",
    software: "Premiere Pro, After Effects",
    description: "A cinematic brand film designed to highlight the emotional tone and campaign positioning of a modern creative studio."
  },
  {
    title: "Apex Social Campaign",
    category: "Graphic Design",
    image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
    client: "Apex Media",
    software: "Photoshop, Illustrator",
    description: "A complete set of social media design assets and branded communication visuals for a lifestyle-focused launch campaign."
  },
  {
    title: "Motion Identity",
    category: "Animation",
    image: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80",
    client: "Nexus Lab",
    software: "After Effects, Cinema 4D",
    description: "A motion graphics identity piece combining typography, transitions, and layered visual storytelling for a digital product reveal."
  },
  {
    title: "Studio Launch Site",
    category: "Web Projects",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    client: "Studio North",
    software: "HTML, CSS, JavaScript, React",
    description: "A premium responsive portfolio website concept created to elevate the studio's online presence and conversion-ready inquiries."
  },
  {
    title: "Wedding Frames",
    category: "Photography",
    image: "https://images.unsplash.com/photo-1520854221256-17451cc331bf?auto=format&fit=crop&w=1200&q=80",
    client: "Private Event",
    software: "Capture One, Lightroom",
    description: "A warm, high-end wedding photography collection celebrating intimate moments, candid expressions, and detailed visual storytelling."
  }
];

const portfolioGrid = document.getElementById("portfolioGrid");
const filterButtons = document.querySelectorAll(".filter-btn");
const projectModal = document.getElementById("projectModal");
const modalImage = document.getElementById("modalImage");
const modalTitle = document.getElementById("modalTitle");
const modalCategory = document.getElementById("modalCategory");
const modalClient = document.getElementById("modalClient");
const modalType = document.getElementById("modalType");
const modalSoftware = document.getElementById("modalSoftware");
const modalDescription = document.getElementById("modalDescription");
const modalClose = document.querySelector(".modal-close");
const navToggle = document.querySelector(".nav-toggle");
const siteNav = document.querySelector(".site-nav");
const form = document.getElementById("contactForm");
const formMessage = document.querySelector(".form-msg");
const dynamicText = document.querySelector(".dynamic-text");
const revealEls = document.querySelectorAll(".reveal");
const photoLightbox = document.getElementById("photoLightbox");
const lightboxImage = document.getElementById("lightboxImage");
const photoLightboxClose = document.querySelector("#photoLightbox .lightbox-close");
const testimonialCards = document.querySelectorAll(".testimonial-card");

function renderPortfolio(filter = "all") {
  portfolioGrid.innerHTML = "";

  const filteredItems = filter === "all"
    ? portfolioItems
    : portfolioItems.filter((item) => item.category === filter);

  filteredItems.forEach((item) => {
    const card = document.createElement("article");
    card.className = "project-card reveal";
    card.innerHTML = `
      <div class="project-media">
        <img src="${item.image}" alt="${item.title}" loading="lazy" />
      </div>
      <div class="project-body">
        <span class="project-tag">${item.category}</span>
        <h3>${item.title}</h3>
        <p>${item.description}</p>
        <div class="project-meta">
          <span>${item.client}</span>
          <button class="btn btn-secondary project-btn" type="button">View Project</button>
        </div>
      </div>
    `;

    const openButton = card.querySelector(".project-btn");
    openButton.addEventListener("click", () => openProjectModal(item));

    portfolioGrid.appendChild(card);
  });

  observeReveal();
}

function openProjectModal(item) {
  modalImage.src = item.image;
  modalImage.alt = item.title;
  modalTitle.textContent = item.title;
  modalCategory.textContent = item.category;
  modalClient.textContent = item.client;
  modalType.textContent = item.category;
  modalSoftware.textContent = item.software;
  modalDescription.textContent = item.description;
  projectModal.classList.add("open");
  projectModal.setAttribute("aria-hidden", "false");
}

function closeProjectModal() {
  projectModal.classList.remove("open");
  projectModal.setAttribute("aria-hidden", "true");
}

function setupFilterButtons() {
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      filterButtons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      renderPortfolio(button.dataset.filter);
    });
  });
}

function animateCounter(element) {
  const target = Number(element.dataset.target);
  const duration = 1400;
  const startTime = performance.now();

  function update(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(target * eased);
    element.textContent = `${value}${target >= 100 ? "+" : ""}`;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = `${target}${target >= 100 ? "+" : ""}`;
    }
  }

  requestAnimationFrame(update);
}

function setupCounters() {
  const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  document.querySelectorAll(".stat-number, [data-target]").forEach((el) => {
    counterObserver.observe(el);
  });
}

function setupDynamicText() {
  if (!dynamicText) return;

  const texts = JSON.parse(dynamicText.dataset.texts || '[]');
  let index = 0;

  setInterval(() => {
    index = (index + 1) % texts.length;
    dynamicText.textContent = texts[index];
  }, 1800);
}

function observeReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.18 });

  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
}

function setupNav() {
  navToggle?.addEventListener("click", () => {
    const expanded = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!expanded));
    siteNav.classList.toggle("open");
  });

  siteNav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      siteNav.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
}

function setupMasonryLightbox() {
  document.querySelectorAll(".masonry-item").forEach((item) => {
    item.addEventListener("click", () => {
      const img = item.querySelector("img");
      if (!img) return;
      lightboxImage.src = img.src;
      lightboxImage.alt = img.alt;
      photoLightbox.classList.add("open");
      photoLightbox.setAttribute("aria-hidden", "false");
    });
  });

  photoLightboxClose?.addEventListener("click", () => {
    photoLightbox.classList.remove("open");
    photoLightbox.setAttribute("aria-hidden", "true");
  });

  photoLightbox.addEventListener("click", (event) => {
    if (event.target === photoLightbox) {
      photoLightbox.classList.remove("open");
      photoLightbox.setAttribute("aria-hidden", "true");
    }
  });
}

function setupTestimonials() {
  if (!testimonialCards.length) return;

  let activeIndex = 0;

  setInterval(() => {
    activeIndex = (activeIndex + 1) % testimonialCards.length;
    testimonialCards.forEach((card, index) => {
      card.classList.toggle("active", index === activeIndex);
    });
  }, 4200);
}

function validateField(input) {
  const isRequired = input.hasAttribute("required");
  const value = input.value.trim();

  if (isRequired && !value) {
    return "This field is required.";
  }

  if (input.type === "email" && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    return "Please enter a valid email address.";
  }

  if (input.name === "phone" && value && !/^[+()\d\s-]{7,}$/.test(value)) {
    return "Please enter a valid phone number.";
  }

  return "";
}

function setupFormValidation() {
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    formMessage.classList.remove("error", "success");

    let hasError = false;
    const fields = form.querySelectorAll("input, textarea");

    fields.forEach((field) => {
      const error = validateField(field);
      if (error) {
        hasError = true;
        field.setAttribute("aria-invalid", "true");
      } else {
        field.setAttribute("aria-invalid", "false");
      }
    });

    if (hasError) {
      formMessage.textContent = "Please fill in the required fields correctly.";
      formMessage.classList.add("error");
      return;
    }

    formMessage.textContent = "Thanks! Your message has been sent successfully.";
    formMessage.classList.add("success");
    form.reset();
  });
}

modalClose?.addEventListener("click", closeProjectModal);
projectModal?.addEventListener("click", (event) => {
  if (event.target === projectModal) closeProjectModal();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeProjectModal();
    photoLightbox.classList.remove("open");
    photoLightbox.setAttribute("aria-hidden", "true");
  }
});

setupFilterButtons();
setupCounters();
setupDynamicText();
setupNav();
setupMasonryLightbox();
setupTestimonials();
setupFormValidation();
renderPortfolio();
