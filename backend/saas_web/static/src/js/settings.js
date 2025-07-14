function showTab(tabName) {
  console.log("[Settings] Switching to tab:", tabName);

  // Hide all tab contents
  const tabs = document.querySelectorAll(".tab-content");
  tabs.forEach((tab) => {
    tab.classList.remove("active");
    console.log("[Settings] Hiding tab:", tab.id);
  });

  // Remove active class from all sidebar items
  const sidebarItems = document.querySelectorAll(".sidebar-item");
  sidebarItems.forEach((item) => item.classList.remove("active"));

  // Show selected tab
  const selectedTab = document.getElementById(tabName);
  if (selectedTab) {
    selectedTab.classList.add("active");
    console.log("[Settings] Showing tab:", tabName);
  } else {
    console.error("[Settings] Tab not found:", tabName);
    // Liste tous les tabs disponibles
    console.log(
      "[Settings] Available tabs:",
      Array.from(tabs).map((t) => t.id)
    );
  }

  // Add active class to clicked sidebar item
  if (event && event.target) {
    const button = event.target.closest(".sidebar-item");
    if (button) button.classList.add("active");
  }

  // Update breadcrumb and header tabs
  updateHeaderForTab(tabName);
}

function updateHeaderForTab(tabName) {
  const breadcrumb = document.querySelector(".breadcrumb-nav .active");

  // Update breadcrumb
  if (breadcrumb) {
    if (tabName === "general-settings" || tabName === "general") {
      breadcrumb.textContent = "Paramètres généraux";
    } else if (tabName.startsWith("app-")) {
      const appName = tabName.replace("app-", "").replace(/-/g, " ");
      breadcrumb.textContent =
        appName.charAt(0).toUpperCase() + appName.slice(1);
    }
  }

  // Update header tabs visibility
  const settingsTabs = document.querySelector(".settings-tabs");
  if (settingsTabs) {
    if (tabName === "general-settings" || tabName === "general") {
      settingsTabs.style.display = "block";
    } else {
      settingsTabs.style.display = "none";
    }
  }

  // Update top tabs active state
  const settingsTabButtons = document.querySelectorAll(".settings-tab");
  settingsTabButtons.forEach((tab) => tab.classList.remove("active"));

  if (tabName === "general-settings" || tabName === "general") {
    const generalTab = document.querySelector(".settings-tab");
    if (generalTab) generalTab.classList.add("active");
  }
}

function showSubTab(subTabName) {
  console.log("[Settings] Switching to sub-tab:", subTabName);

  // Hide all tab contents
  const tabContents = document.querySelectorAll(".tab-content");
  tabContents.forEach((content) => content.classList.remove("active"));

  // Remove active class from all tabs
  const tabs = document.querySelectorAll(".settings-tab");
  tabs.forEach((tab) => tab.classList.remove("active"));

  // Show selected tab content
  const selectedContent = document.getElementById(subTabName);
  if (selectedContent) {
    selectedContent.classList.add("active");
  }

  // Add active class to clicked tab
  if (event && event.target) {
    const button = event.target.closest(".settings-tab");
    if (button) {
      button.classList.add("active");
    }
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", function () {
  updateHeaderForTab("general-settings");

  // Set initial active states
  const firstSidebarItem = document.querySelector(".sidebar-item");
  if (firstSidebarItem) {
    firstSidebarItem.classList.add("active");
  }

  // Initialize first tab as active
  const userProfileTab = document.getElementById("user-profile");
  if (userProfileTab) {
    userProfileTab.classList.add("active");
  }
});

// Account management functions
async function suspendAccount() {
  if (
    confirm(
      "Êtes-vous sûr de vouloir suspendre temporairement votre compte ? Vous pourrez le réactiver à tout moment."
    )
  ) {
    try {
      showTemporaryMessage("Suspension du compte en cours...", "info");

      const response = await fetch("/auth/api/suspend-account/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();

      if (result.success) {
        showTemporaryMessage(
          "Compte suspendu avec succès. Vous allez être déconnecté.",
          "success"
        );
        setTimeout(() => {
          window.location.href = "/auth/logout/";
        }, 2000);
      } else {
        showTemporaryMessage(
          "Erreur lors de la suspension: " +
            (result.error || "Erreur inconnue"),
          "error"
        );
      }
    } catch (error) {
      console.error("Suspension error:", error);
      showTemporaryMessage(
        "Erreur de connexion lors de la suspension",
        "error"
      );
    }
  }
}

async function exportData() {
  if (confirm("Souhaitez-vous exporter toutes vos données personnelles ?")) {
    try {
      showTemporaryMessage("Export des données en cours...", "info");

      const response = await fetch("/auth/api/export-data/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();

      if (result.success) {
        showTemporaryMessage(
          "Export demandé avec succès ! Vous recevrez un email avec vos données dans quelques minutes.",
          "success"
        );

        // Si l'API retourne directement un lien de téléchargement
        if (result.download_url) {
          const link = document.createElement("a");
          link.href = result.download_url;
          link.download = `linguify_data_export_${
            new Date().toISOString().split("T")[0]
          }.json`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
      } else {
        showTemporaryMessage(
          "Erreur lors de l'export: " + (result.error || "Erreur inconnue"),
          "error"
        );
      }
    } catch (error) {
      console.error("Export error:", error);
      showTemporaryMessage("Erreur de connexion lors de l'export", "error");
    }
  }
}

async function deleteAccount() {
  const confirmText = "SUPPRIMER";
  const userInput = prompt(
    `⚠️ ATTENTION : Cette action est irréversible !\n\n` +
      `Toutes vos données seront définitivement supprimées :\n` +
      `• Profil utilisateur\n` +
      `• Progression d'apprentissage\n` +
      `• Notes et flashcards\n` +
      `• Historique d'activité\n\n` +
      `Pour confirmer, tapez exactement : ${confirmText}`
  );

  if (userInput === confirmText) {
    if (
      confirm(
        "Dernière confirmation : êtes-vous absolument certain de vouloir supprimer votre compte ?"
      )
    ) {
      try {
        showTemporaryMessage("Suppression du compte en cours...", "warning");

        const response = await fetch("/auth/api/delete-account/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCsrfToken(),
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            confirmation: confirmText,
            immediate: false, // Utilise la période de grâce de 30 jours
          }),
        });

        const result = await response.json();

        if (result.success) {
          alert(
            `Votre compte a été programmé pour suppression.\n\n` +
              `• Date de suppression : ${new Date(
                result.deletion_date
              ).toLocaleDateString("fr-FR")}\n` +
              `• Vous avez ${result.days_remaining} jours pour annuler\n` +
              `• Un email de confirmation vous a été envoyé\n\n` +
              `Vous pouvez annuler cette suppression en vous reconnectant avant la date limite.`
          );

          setTimeout(() => {
            window.location.href = "/auth/logout/";
          }, 3000);
        } else {
          showTemporaryMessage(
            "Erreur lors de la suppression: " +
              (result.error || "Erreur inconnue"),
            "error"
          );
        }
      } catch (error) {
        console.error("Account deletion error:", error);
        showTemporaryMessage(
          "Erreur de connexion lors de la suppression",
          "error"
        );
      }
    }
  } else if (userInput !== null) {
    alert("Texte de confirmation incorrect. Suppression annulée.");
  }
}

async function changePassword() {
  // Créer un modal pour le changement de mot de passe
  const modalHtml = `
        <div class="modal fade" id="changePasswordModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Changer le mot de passe</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="changePasswordForm">
                            <div class="form-group mb-3">
                                <label class="form-label">Mot de passe actuel</label>
                                <input type="password" id="currentPassword" class="form-control" required>
                            </div>
                            <div class="form-group mb-3">
                                <label class="form-label">Nouveau mot de passe</label>
                                <input type="password" id="newPassword" class="form-control" required>
                                <div class="help-text">Au moins 8 caractères avec lettres et chiffres</div>
                            </div>
                            <div class="form-group mb-3">
                                <label class="form-label">Confirmer le nouveau mot de passe</label>
                                <input type="password" id="confirmPassword" class="form-control" required>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-secondary" data-bs-dismiss="modal">Annuler</button>
                        <button type="button" class="btn-primary" onclick="submitPasswordChange()">Changer le mot de passe</button>
                    </div>
                </div>
            </div>
        </div>
    `;

  // Ajouter le modal au DOM s'il n'existe pas
  if (!document.getElementById("changePasswordModal")) {
    document.body.insertAdjacentHTML("beforeend", modalHtml);
  }

  // Afficher le modal
  const modal = new bootstrap.Modal(
    document.getElementById("changePasswordModal")
  );
  modal.show();
}

async function submitPasswordChange() {
  const currentPassword = document.getElementById("currentPassword").value;
  const newPassword = document.getElementById("newPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (newPassword !== confirmPassword) {
    showTemporaryMessage("Les mots de passe ne correspondent pas", "error");
    return;
  }

  if (newPassword.length < 8) {
    showTemporaryMessage(
      "Le mot de passe doit contenir au moins 8 caractères",
      "error"
    );
    return;
  }

  try {
    showTemporaryMessage("Changement du mot de passe...", "info");

    const response = await fetch("/auth/api/change-password/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCsrfToken(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const result = await response.json();

    if (result.success) {
      showTemporaryMessage("Mot de passe changé avec succès !", "success");
      bootstrap.Modal.getInstance(
        document.getElementById("changePasswordModal")
      ).hide();
      document.getElementById("changePasswordForm").reset();
    } else {
      showTemporaryMessage(
        "Erreur: " + (result.error || "Mot de passe actuel incorrect"),
        "error"
      );
    }
  } catch (error) {
    console.error("Password change error:", error);
    showTemporaryMessage("Erreur de connexion", "error");
  }
}

async function logoutAllDevices() {
  if (
    confirm(
      "Êtes-vous sûr de vouloir déconnecter tous vos appareils ? Vous devrez vous reconnecter sur chaque appareil."
    )
  ) {
    try {
      showTemporaryMessage("Déconnexion de tous les appareils...", "info");

      const response = await fetch("/auth/api/logout-all/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/json",
        },
      });

      const result = await response.json();

      if (result.success) {
        showTemporaryMessage(
          "Tous les appareils ont été déconnectés. Vous allez être redirigé...",
          "success"
        );
        setTimeout(() => {
          window.location.href = "/auth/login/";
        }, 2000);
      } else {
        showTemporaryMessage(
          "Erreur: " + (result.error || "Erreur inconnue"),
          "error"
        );
      }
    } catch (error) {
      console.error("Logout all devices error:", error);
      showTemporaryMessage("Erreur de connexion", "error");
    }
  }
}

// Theme selection function
function selectTheme(element, theme) {
  // Update visual selection
  document
    .querySelectorAll('label[onclick*="selectTheme"]')
    .forEach((label) => {
      label.style.borderColor = "#dee2e6";
      label.style.backgroundColor = "";
    });
  element.style.borderColor = "#875a7b";
  element.style.backgroundColor = "rgba(135, 90, 123, 0.05)";

  // Apply theme preview (optional)
  if (theme === "dark") {
    document.body.style.filter = "invert(0.1)";
  } else {
    document.body.style.filter = "";
  }
}

// Settings reset function
function resetSettings() {
  if (
    confirm(
      "Êtes-vous sûr de vouloir réinitialiser tous les paramètres généraux aux valeurs par défaut ?"
    )
  ) {
    // Reset form to defaults
    const form = document.querySelector("#general-settings form");
    if (form) {
      // Reset theme to light
      form.querySelector('input[name="theme"][value="light"]').checked = true;
      // Reset accent color to purple
      form.querySelector(
        'input[name="accent_color"][value="purple"]'
      ).checked = true;
      // Reset checkboxes
      form.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
        checkbox.checked = false;
      });
      // Reset selects to default values
      form.querySelector('select[name="font_size"]').value = "medium";
      form.querySelector('select[name="menu_layout"]').value = "sidebar";

      alert(
        "Paramètres réinitialisés. N'oubliez pas de sauvegarder pour appliquer les changements."
      );
    }
  }
}

// Voice settings functions
function testVoice() {
  const utterance = new SpeechSynthesisUtterance(
    "Test de l'assistant vocal Linguify. Votre configuration fonctionne correctement !"
  );

  // Apply current settings
  const voiceSpeed =
    document.querySelector('select[name="preferred_voice_speed"]')?.value ||
    "normal";
  const voicePitch =
    document.querySelector('input[name="preferred_voice_pitch"]')?.value || 50;

  // Set speech parameters
  switch (voiceSpeed) {
    case "slow":
      utterance.rate = 0.7;
      break;
    case "fast":
      utterance.rate = 1.3;
      break;
    default:
      utterance.rate = 1.0;
  }

  utterance.pitch = voicePitch / 50; // Convert 0-100 to 0-2
  utterance.lang = "fr-FR";

  speechSynthesis.speak(utterance);
}

function testMicrophone() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Votre navigateur ne supporte pas l'accès au microphone.");
    return;
  }

  navigator.mediaDevices
    .getUserMedia({ audio: true })
    .then((stream) => {
      // Test successful
      alert("Microphone détecté et fonctionnel ! 🎤");

      // Stop the stream
      stream.getTracks().forEach((track) => track.stop());

      // Optional: Show volume levels for a few seconds
      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      microphone.connect(analyser);

      // Simple volume indicator for 3 seconds
      let countdown = 30;
      const volumeTest = setInterval(() => {
        analyser.getByteFrequencyData(dataArray);
        const volume = dataArray.reduce((a, b) => a + b) / dataArray.length;

        if (countdown-- <= 0) {
          clearInterval(volumeTest);
          audioContext.close();
        }
      }, 100);
    })
    .catch((error) => {
      console.error("Erreur microphone:", error);
      alert(
        "Impossible d'accéder au microphone. Vérifiez les permissions de votre navigateur."
      );
    });
}

function resetVoiceSettings() {
  if (
    confirm(
      "Êtes-vous sûr de vouloir réinitialiser tous les paramètres vocaux aux valeurs par défaut ?"
    )
  ) {
    const form = document.querySelector("#voice-settings form");
    if (form) {
      // Reset voice settings to defaults
      form.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
        // Default enabled: tts_enabled, voice_commands_enabled, noise_suppression, pronunciation_feedback
        const defaultEnabled = [
          "tts_enabled",
          "voice_commands_enabled",
          "noise_suppression",
          "pronunciation_feedback",
        ];
        checkbox.checked = defaultEnabled.includes(checkbox.name);
      });

      // Reset voice speed to normal
      form.querySelector('select[name="preferred_voice_speed"]').value =
        "normal";

      // Reset pitch to 50
      form.querySelector('input[name="preferred_voice_pitch"]').value = 50;

      // Reset sensitivity to 70
      form.querySelector('input[name="sensitivity"]').value = 70;

      // Reset accent to auto
      form.querySelector('select[name="preferred_accent"]').value = "";

      alert(
        "Paramètres vocaux réinitialisés. N'oubliez pas de sauvegarder pour appliquer les changements."
      );
    }
  }
}

// Form validation and real-time feedback
function initializeFormValidation() {
  // Username validation
  const usernameField = document.querySelector('input[name="username"]');
  if (usernameField) {
    usernameField.addEventListener("input", validateUsername);
    usernameField.addEventListener("blur", validateUsername);
  }

  // Email validation (read-only, but for consistency)
  const emailField = document.querySelector('input[type="email"]');
  if (emailField) {
    emailField.addEventListener("blur", validateEmail);
  }

  // Phone number validation
  const phoneField = document.querySelector('input[name="phone_number"]');
  if (phoneField) {
    phoneField.addEventListener("input", validatePhoneNumber);
    phoneField.addEventListener("blur", validatePhoneNumber);
  }

  // File upload validation
  const profilePictureInput = document.querySelector(
    'input[name="profile_picture"]'
  );
  if (profilePictureInput) {
    profilePictureInput.addEventListener("change", validateProfilePicture);
  }

  // Voice settings real-time updates
  initializeVoiceSettingsPreview();

  // Password strength (if password fields exist)
  initializePasswordValidation();
}

function validateUsername(event) {
  const input = event.target;
  const value = input.value.trim();
  const feedback = getOrCreateFeedback(input, "username-feedback");

  // Reset styling
  input.classList.remove("is-invalid", "is-valid");

  if (value.length === 0) {
    feedback.textContent = "";
    return;
  }

  if (value.length < 3) {
    showFieldError(
      input,
      feedback,
      "Le nom d'utilisateur doit contenir au moins 3 caractères"
    );
    return;
  }

  if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
    showFieldError(
      input,
      feedback,
      "Seuls les lettres, chiffres, tirets et underscores sont autorisés"
    );
    return;
  }

  // Vérification async de la disponibilité (si pas le nom actuel)
  const currentUsername = input.getAttribute("data-current-username") || "";
  if (value !== currentUsername && value.length >= 3) {
    checkUsernameAvailability(value, input, feedback);
  } else {
    showFieldSuccess(input, feedback, "Nom d'utilisateur valide");
  }
}

function validateEmail(event) {
  const input = event.target;
  const value = input.value.trim();
  const feedback = getOrCreateFeedback(input, "email-feedback");

  if (value.length === 0) return;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value)) {
    showFieldError(input, feedback, "Format d'email invalide");
  } else {
    showFieldSuccess(input, feedback, "Email valide");
  }
}

function validatePhoneNumber(event) {
  const input = event.target;
  const value = input.value.trim();
  const feedback = getOrCreateFeedback(input, "phone-feedback");

  // Reset styling
  input.classList.remove("is-invalid", "is-valid");

  if (value.length === 0) {
    feedback.textContent = "";
    return;
  }

  // Phone number regex: + followed by country code and number
  const phoneRegex = /^\+\d{1,4}[\s\-\(\)]*[\d\s\-\(\)]{8,}$/;
  if (!phoneRegex.test(value)) {
    showFieldError(
      input,
      feedback,
      "Format invalide. Utilisez +32 123 456 789"
    );
  } else {
    showFieldSuccess(input, feedback, "Numéro de téléphone valide");
  }
}

function validateProfilePicture(event) {
  const input = event.target;
  const file = input.files[0];
  const feedback = getOrCreateFeedback(input, "picture-feedback");

  console.log("[ProfilePicture] File selection event triggered");

  if (!file) {
    console.log("[ProfilePicture] No file selected, resetting");
    feedback.textContent = "";
    input.classList.remove("is-invalid", "is-valid");
    resetProfilePicturePreview();
    return;
  }

  console.log("[ProfilePicture] File selected:", {
    name: file.name,
    size: file.size,
    type: file.type,
    lastModified: new Date(file.lastModified),
  });

  // Vérifier le type de fichier
  const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    console.warn("[ProfilePicture] Invalid file type:", file.type);
    showFieldError(
      input,
      feedback,
      "Format non supporté. Utilisez JPG, PNG ou WEBP"
    );
    resetProfilePicturePreview();
    return;
  }
  console.log("[ProfilePicture] File type validation passed");

  // Vérifier la taille (5MB max)
  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    console.warn(
      "[ProfilePicture] File too large:",
      `${file.size} bytes > ${maxSize} bytes`
    );
    showFieldError(input, feedback, "Fichier trop volumineux. Maximum 5MB");
    resetProfilePicturePreview();
    return;
  }
  console.log("[ProfilePicture] File size validation passed");

  showFieldSuccess(
    input,
    feedback,
    `Image valide (${(file.size / 1024 / 1024).toFixed(1)}MB)`
  );
  console.log("[ProfilePicture] Validation successful, starting preview");

  // Prévisualisation de l'image
  previewProfilePicture(file);
}

function previewProfilePicture(file) {
  console.log("[ProfilePicture] Starting preview for file:", file.name);
  const reader = new FileReader();

  reader.onload = function (e) {
    console.log("[ProfilePicture] File read successfully, updating avatars");
    // Trouver tous les avatars utilisateur et les mettre à jour
    const avatars = document.querySelectorAll(".user-avatar img");
    console.log(
      "[ProfilePicture] Found",
      avatars.length,
      "avatar images to update"
    );

    avatars.forEach((avatar, index) => {
      console.log(`[ProfilePicture] Updating avatar ${index + 1}:`, avatar);
      avatar.src = e.target.result;
    });
    console.log("[ProfilePicture] Preview update complete");
  };

  reader.onerror = function (e) {
    console.error("[ProfilePicture] Error reading file:", e);
  };

  reader.readAsDataURL(file);
}

function resetProfilePicturePreview() {
  // Remettre l'image originale ou les initiales
  const avatars = document.querySelectorAll(".user-avatar img");
  avatars.forEach((avatar) => {
    const originalSrc = avatar.getAttribute("data-original-src");
    if (originalSrc) {
      avatar.src = originalSrc;
    } else {
      // Si pas d'image, remettre les initiales
      const avatarContainer = avatar.parentElement;
      const initials = avatarContainer.getAttribute("data-initials");
      if (initials) {
        avatarContainer.innerHTML = initials;
      }
    }
  });
}

function initializeVoiceSettingsPreview() {
  // Sliders avec preview temps réel
  const pitchSlider = document.querySelector(
    'input[name="preferred_voice_pitch"]'
  );
  const sensitivitySlider = document.querySelector('input[name="sensitivity"]');

  if (pitchSlider) {
    pitchSlider.addEventListener("input", (e) => {
      const value = e.target.value;
      const label = e.target.parentNode.querySelector(".form-label");
      if (label) {
        label.textContent = `Hauteur de voix (${value}%)`;
      }
    });
  }

  if (sensitivitySlider) {
    sensitivitySlider.addEventListener("input", (e) => {
      const value = e.target.value;
      const label = e.target.parentNode.querySelector(".form-label");
      if (label) {
        label.textContent = `Sensibilité du microphone (${value}%)`;
      }
    });
  }

  // Aperçu en temps réel du thème
  const themeRadios = document.querySelectorAll('input[name="theme"]');
  themeRadios.forEach((radio) => {
    radio.addEventListener("change", previewTheme);
  });
}

function initializePasswordValidation() {
  // Si des champs de mot de passe existent dans le futur
  const passwordFields = document.querySelectorAll('input[type="password"]');
  passwordFields.forEach((field) => {
    field.addEventListener("input", validatePasswordStrength);
  });
}

async function checkUsernameAvailability(username, input, feedback) {
  try {
    showFieldPending(input, feedback, "Vérification de la disponibilité...");

    const response = await fetch(
      `/api/check-username/?username=${encodeURIComponent(username)}`,
      {
        method: "GET",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/json",
        },
      }
    );

    const data = await response.json();

    if (data.available) {
      showFieldSuccess(input, feedback, data.message);
    } else {
      showFieldError(input, feedback, data.message);
    }
  } catch (error) {
    console.error("Username check error:", error);
    showFieldError(input, feedback, "Erreur lors de la vérification");
  }
}

function previewProfilePicture(file) {
  const reader = new FileReader();
  reader.onload = function (e) {
    // Trouver tous les avatars à mettre à jour
    const avatars = document.querySelectorAll(".user-avatar img, .user-avatar");
    avatars.forEach((avatar) => {
      if (avatar.tagName === "IMG") {
        avatar.src = e.target.result;
      } else {
        // Remplacer le contenu texte par l'image
        avatar.innerHTML = `<img src="${e.target.result}" alt="Aperçu" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
      }
    });
  };
  reader.readAsDataURL(file);
}

function previewTheme(event) {
  const theme = event.target.value;
  const body = document.body;

  // Appliquer temporairement le thème pour aperçu
  body.classList.remove("theme-light", "theme-dark", "theme-auto");

  if (theme === "dark") {
    body.classList.add("theme-dark");
    body.style.filter = "invert(0.05)";
  } else if (theme === "light") {
    body.classList.add("theme-light");
    body.style.filter = "none";
  } else {
    body.classList.add("theme-auto");
    body.style.filter = "none";
  }
}

// Fonctions utilitaires pour le feedback
function getOrCreateFeedback(input, id) {
  let feedback = document.getElementById(id);
  if (!feedback) {
    feedback = document.createElement("div");
    feedback.id = id;
    feedback.className = "form-feedback";
    feedback.style.fontSize = "12px";
    feedback.style.marginTop = "4px";
    input.parentNode.appendChild(feedback);
  }
  return feedback;
}

function showFieldError(input, feedback, message) {
  input.classList.remove("is-valid", "is-pending");
  input.classList.add("is-invalid");
  feedback.textContent = message;
  feedback.style.color = "#dc3545";
}

function showFieldSuccess(input, feedback, message) {
  input.classList.remove("is-invalid", "is-pending");
  input.classList.add("is-valid");
  feedback.textContent = message;
  feedback.style.color = "#198754";
}

function showFieldPending(input, feedback, message) {
  input.classList.remove("is-invalid", "is-valid");
  input.classList.add("is-pending");
  feedback.textContent = message;
  feedback.style.color = "#6c757d";
}

// Form submission validation
function validateFormBeforeSubmit(form) {
  const invalidFields = form.querySelectorAll(".is-invalid");

  if (invalidFields.length > 0) {
    // Scroll to first invalid field
    invalidFields[0].scrollIntoView({ behavior: "smooth", block: "center" });
    invalidFields[0].focus();

    showNotification(
      "Veuillez corriger les erreurs avant de continuer",
      "error"
    );
    return false;
  }

  return true;
}

// Auto-save functionality (draft)
function initializeAutoSave() {
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    const inputs = form.querySelectorAll("input, select, textarea");
    inputs.forEach((input) => {
      if (input.type !== "file" && input.type !== "submit") {
        input.addEventListener("change", () => saveDraft(form));
      }
    });
  });
}

async function saveDraft(form) {
  const formData = new FormData(form);
  const draftData = {};
  const settingsType =
    form.querySelector('input[name="settings_type"]')?.value || "profile";

  for (let [key, value] of formData.entries()) {
    if (key !== "csrfmiddlewaretoken" && key !== "profile_picture") {
      draftData[key] = value;
    }
  }

  try {
    // Sauvegarder à la fois localement et sur le serveur
    localStorage.setItem(
      `settings_draft_${settingsType}`,
      JSON.stringify(draftData)
    );

    const response = await fetch("/api/save-draft/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCsrfToken(),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: settingsType,
        data: draftData,
      }),
    });

    const result = await response.json();

    if (result.success) {
      showAutoSaveIndicator("saved");
    } else {
      console.warn("Server draft save failed:", result.error);
      showTemporaryMessage("Brouillon sauvé localement", "warning");
    }
  } catch (error) {
    console.error("Draft save error:", error);
    showTemporaryMessage("Brouillon sauvé localement", "warning");
  }
}

async function loadDraft(settingsType = "profile") {
  try {
    // Essayer de charger depuis le serveur d'abord
    const response = await fetch(`/api/load-draft/?type=${settingsType}`, {
      method: "GET",
      headers: {
        "X-CSRFToken": getCsrfToken(),
        "Content-Type": "application/json",
      },
    });

    const result = await response.json();

    let draftData = null;
    if (result.success && result.draft) {
      draftData = result.draft.data;
      showTemporaryMessage("Brouillon chargé depuis le serveur", "info");
    } else {
      // Fallback vers le stockage local
      const localDraft = localStorage.getItem(`settings_draft_${settingsType}`);
      if (localDraft) {
        draftData = JSON.parse(localDraft);
        showTemporaryMessage("Brouillon chargé localement", "info");
      }
    }

    if (draftData) {
      Object.entries(draftData).forEach(([key, value]) => {
        const input = document.querySelector(`[name="${key}"]`);
        if (input) {
          if (input.type === "checkbox") {
            input.checked = value === "on";
          } else {
            input.value = value;
          }
        }
      });
    }
  } catch (error) {
    console.error("Error loading draft:", error);
    // Fallback vers le stockage local en cas d'erreur
    const localDraft = localStorage.getItem(`settings_draft_${settingsType}`);
    if (localDraft) {
      try {
        const data = JSON.parse(localDraft);
        Object.entries(data).forEach(([key, value]) => {
          const input = document.querySelector(`[name="${key}"]`);
          if (input) {
            if (input.type === "checkbox") {
              input.checked = value === "on";
            } else {
              input.value = value;
            }
          }
        });
        showTemporaryMessage("Brouillon chargé localement", "warning");
      } catch (parseError) {
        console.error("Error parsing local draft:", parseError);
      }
    }
  }
}

function clearDraft(settingsType = "profile") {
  localStorage.removeItem(`settings_draft_${settingsType}`);
}

function getCsrfToken() {
  return (
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie.match(/csrftoken=([^;]+)/)?.[1]
  );
}

function showAutoSaveIndicator(status) {
  let indicator = document.getElementById("auto-save-indicator");
  if (!indicator) {
    indicator = document.createElement("div");
    indicator.id = "auto-save-indicator";
    indicator.className = "auto-save-indicator";
    document.body.appendChild(indicator);
  }

  indicator.classList.remove("saving", "saved", "hidden");

  if (status === "saving") {
    indicator.textContent = "💾 Sauvegarde...";
    indicator.classList.add("saving");
  } else if (status === "saved") {
    indicator.textContent = "✅ Sauvegardé";
    indicator.classList.add("saved");
    setTimeout(() => {
      indicator.classList.add("hidden");
    }, 2000);
  }
}

function updateAllProfilePictures(newUrl) {
  console.log("[ProfilePicture] Updating all profile pictures to:", newUrl);
  
  // Update all user avatar images throughout the page
  const avatars = document.querySelectorAll(".user-avatar img");
  avatars.forEach((avatar, index) => {
    console.log(`[ProfilePicture] Updating avatar ${index + 1}:`, avatar);
    avatar.src = newUrl;
    // Also update the data-original-src attribute
    avatar.setAttribute("data-original-src", newUrl);
  });
  
  // Update any other profile picture elements
  const otherProfileImages = document.querySelectorAll('img[alt*="Photo de profil"], img[alt*="profile"]');
  otherProfileImages.forEach((img, index) => {
    console.log(`[ProfilePicture] Updating profile image ${index + 1}:`, img);
    img.src = newUrl;
  });
  
  console.log(`[ProfilePicture] Updated ${avatars.length + otherProfileImages.length} profile picture elements`);
}

function showTemporaryMessage(message, type) {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText =
    "top: 20px; right: 20px; z-index: 9999; max-width: 300px;";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
  document.body.appendChild(alertDiv);

  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 3000);
}

// Initialize everything when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  // Initialize validation after a short delay to ensure all elements are loaded
  setTimeout(() => {
    initializeFormValidation();
    initializeAutoSave();

    // Load draft if available
    if (localStorage.getItem("settings_draft")) {
      loadDraft();
    }

    // Handle form submission with AJAX
    document.querySelectorAll("form").forEach((form) => {
      form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Always prevent default form submission
        console.log("[Form] Submit event triggered");

        // Log form data
        const formData = new FormData(this);
        const formEntries = {};
        let hasProfilePicture = false;
        
        for (let [key, value] of formData.entries()) {
          if (key === "profile_picture") {
            if (value instanceof File && value.size > 0) {
              formEntries[key] = `File: ${value.name} (${value.size} bytes)`;
              hasProfilePicture = true;
              console.log("[Form] Profile picture file found:", value);
            } else {
              formEntries[key] = `Empty file input`;
              console.log("[Form] Profile picture input is empty or invalid:", value);
            }
          } else {
            formEntries[key] = value;
          }
        }
        console.log("[Form] Form data:", formEntries);
        console.log("[Form] Has profile picture:", hasProfilePicture);

        if (!validateFormBeforeSubmit(this)) {
          console.warn("[Form] Validation failed, preventing submission");
          return;
        }

        try {
          console.log("[Form] Validation passed, submitting via AJAX");
          
          // Show loading message
          showTemporaryMessage("Sauvegarde en cours...", "info");
          
          // Submit form via AJAX
          const response = await fetch(this.action, {
            method: "POST",
            body: formData,
            headers: {
              "X-CSRFToken": getCsrfToken(),
            },
          });

          const result = await response.json();
          
          if (result.success) {
            console.log("[Form] Success:", result.message);
            showTemporaryMessage(result.message, "success");
            clearDraft();
            
            // Update profile picture if a new one was uploaded
            if (result.profile_picture_url) {
              console.log("[Form] Updating profile picture to:", result.profile_picture_url);
              updateAllProfilePictures(result.profile_picture_url);
            }
          } else {
            console.error("[Form] Error:", result.message || result.errors);
            showTemporaryMessage(result.message || "Erreur lors de la sauvegarde", "error");
          }
        } catch (error) {
          console.error("[Form] AJAX Error:", error);
          showTemporaryMessage("Erreur de connexion", "error");
        }
      });
    });
  }, 100);
});

// Debug functions for profile picture testing
window.debugProfilePicture = {
  logFormData: function () {
    const form = document.querySelector("form");
    if (form) {
      const formData = new FormData(form);
      console.log("[DEBUG] Current form data:");
      for (let [key, value] of formData.entries()) {
        if (key === "profile_picture" && value instanceof File) {
          console.log(
            `  ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`
          );
        } else {
          console.log(`  ${key}: ${value}`);
        }
      }
    }
  },

  clearProfilePicture: function () {
    const input = document.querySelector('input[name="profile_picture"]');
    if (input) {
      input.value = "";
      console.log("[DEBUG] Profile picture input cleared");
      resetProfilePicturePreview();
    }
  },

  testValidation: function (file) {
    if (!file) {
      console.log("[DEBUG] No file provided for validation test");
      return;
    }
    console.log("[DEBUG] Testing validation for:", file);
    const event = { target: { files: [file] } };
    validateProfilePicture(event);
  },

  getCurrentUser: function () {
    console.log("[DEBUG] Current user avatar images:");
    document.querySelectorAll(".user-avatar img").forEach((img, i) => {
      console.log(`  Avatar ${i + 1}: ${img.src}`);
    });
  },
};

console.log(
  "[DEBUG] Profile picture debug functions available: window.debugProfilePicture"
);

// Debug function to test if apps are loaded
function debugApps() {
  const appItems = document.querySelectorAll('[id^="app-"]');
  console.log("Apps found:", appItems.length);
  appItems.forEach((app) => {
    console.log("App ID:", app.id);
  });
}
