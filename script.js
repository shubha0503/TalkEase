document.addEventListener("DOMContentLoaded", () => {
  // Navigation and UI elements
  const sections = document.querySelectorAll(".section");
  const navLinks = document.querySelectorAll(".main-nav a");
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
  const header = document.querySelector(".header");
  const logo = document.querySelector(".logo");

  // Chat elements
  const chatBox = document.getElementById("chat-box");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const typingIndicator = document.getElementById("typing-indicator");
  const voiceInputBtn = document.getElementById("voice-input-btn");
  const textToSpeechBtn = document.getElementById("text-to-speech-btn");

  // Lesson elements
  const generateLessonBtn = document.getElementById("generate-lesson-btn");
  const lessonLanguage = document.getElementById("lesson-language");
  const lessonTopic = document.getElementById("lesson-topic");
  const lessonLevel = document.getElementById("lesson-level");
  const lessonResult = document.getElementById("lesson-result");
  const saveLessonBtn = document.getElementById("save-lesson-btn");
  const shareLessonBtn = document.getElementById("share-lesson-btn");
  const speakLessonBtn = document.getElementById("speak-lesson-btn");

  // Audio elements
  const messageSound = document.getElementById("message-sound");
  const notificationSound = document.getElementById("notification-sound");

  // Toast container
  const toastContainer = document.getElementById("toast-container");

  // Mock data for chat responses
  const mockBotResponses = {
      hello: "Hello! How can I help you with your language learning today?",
      hi: "Hi there! Ready to practice some language skills?",
      "how are you": "I'm doing great! More importantly, how is your language learning going?",
      help: "I can help you practice conversations, answer language questions, or suggest learning resources. What would you like to do?",
      goodbye: "Goodbye! Don't forget to practice a little each day. See you next time!",
      "thank you": "You're welcome! Is there anything else you'd like to practice?",
      default: "That's interesting! Would you like to know how to say that in another language?",
  };

  // Initialize the app
  function init() {
      // Set up event listeners
      setupEventListeners();

      // Check for saved theme preference
      checkThemePreference();

      // Show the home section by default
      showSection("home");
      
      // Show welcome toast
      showToast("Welcome to TalkEase!", "success");
  }

  // Set up event listeners
  function setupEventListeners() {
      // Logo click
      logo.addEventListener("click", function() {
          showSection("home");
      });
      
      // Navigation links
      navLinks.forEach((link) => {
          link.addEventListener("click", function (e) {
              e.preventDefault();
              const section = this.getAttribute("href").substring(1);
              showSection(section);
              
              // Close mobile menu if open
              if (header.classList.contains("menu-open")) {
                  header.classList.remove("menu-open");
              }
          });
      });

      // Mobile menu toggle
      if (mobileMenuBtn) {
          mobileMenuBtn.addEventListener("click", toggleMobileMenu);
      }

      // Theme toggle
      if (themeToggleBtn) {
          themeToggleBtn.addEventListener("click", toggleTheme);
      }

      // Chat functionality
      if (sendBtn) {
          sendBtn.addEventListener("click", sendMessage);
      }

      if (chatInput) {
          chatInput.addEventListener("keypress", (e) => {
              if (e.key === "Enter") {
                  sendMessage();
              }
          });
      }

      // Voice input
      if (voiceInputBtn) {
          setupSpeechRecognition();
      }

      // Text to speech
      if (textToSpeechBtn) {
          setupTextToSpeech();
      }

      // Lesson generator
      if (generateLessonBtn) {
          generateLessonBtn.addEventListener("click", generateLesson);
      }

      // Lesson actions
      if (saveLessonBtn) {
          saveLessonBtn.addEventListener("click", saveLesson);
      }

      if (shareLessonBtn) {
          shareLessonBtn.addEventListener("click", shareLesson);
      }

      if (speakLessonBtn) {
          speakLessonBtn.addEventListener("click", speakLesson);
      }

      // Feature card buttons
      document.querySelectorAll('.feature-card').forEach(card => {
          card.addEventListener('click', function() {
              const target = this.getAttribute('data-target');
              if (target) {
                  showSection(target);
              }
          });
          
          // Prevent button click from triggering card click
          const button = card.querySelector('.btn-primary');
          if (button) {
              button.addEventListener('click', function(e) {
                  e.stopPropagation();
                  const target = card.getAttribute('data-target');
                  if (target) {
                      showSection(target);
                  }
              });
          }
      });
      
      // Make badge icons interactive
      document.querySelectorAll('.badge-icon:not(.active)').forEach(badge => {
          badge.addEventListener('click', function() {
              showToast("Keep learning to unlock this badge!", "warning");
          });
      });
      
      // Make leaderboard items interactive
      document.querySelectorAll('.leaderboard-item').forEach(item => {
          item.addEventListener('click', function() {
              const userName = this.querySelector('.user-name').textContent;
              const points = this.querySelector('.points').textContent;
              showToast(`${userName} has earned ${points}`, "info");
          });
      });
  }

  // Show section and update navigation
  function showSection(sectionId) {
      // Hide all sections
      sections.forEach((section) => {
          section.classList.remove("active");
      });

      // Show the selected section
      const selectedSection = document.getElementById(sectionId);
      if (selectedSection) {
          selectedSection.classList.add("active");

          // Update navigation
          navLinks.forEach((link) => {
              link.classList.remove("active");
              if (link.getAttribute("href").substring(1) === sectionId) {
                  link.classList.add("active");
              }
          });

          // Close mobile menu if open
          header.classList.remove("menu-open");

          // Play sound
          playSound("message-sound");
          
          // Show section-specific toast
          if (sectionId === "chat") {
              showToast("Chat with our AI language tutor!", "info");
          } else if (sectionId === "lesson") {
              showToast("Create a custom language lesson!", "info");
          } else if (sectionId === "progress") {
              showToast("Track your learning progress!", "info");
          }
      }
  }

  // Toggle mobile menu
  function toggleMobileMenu() {
      header.classList.toggle("menu-open");
      playSound("message-sound");
  }

  // Toggle theme
  function toggleTheme() {
      document.documentElement.classList.toggle("dark-mode");

      // Update icon
      const themeIcon = themeToggleBtn.querySelector("i");
      if (document.documentElement.classList.contains("dark-mode")) {
          themeIcon.className = "fas fa-sun";
          localStorage.setItem("theme", "dark");
          showToast("Dark mode enabled", "info");
      } else {
          themeIcon.className = "fas fa-moon";
          localStorage.setItem("theme", "light");
          showToast("Light mode enabled", "info");
      }

      // Play sound
      playSound("message-sound");
  }

  // Check for saved theme preference
  function checkThemePreference() {
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme === "dark") {
          document.documentElement.classList.add("dark-mode");
          themeToggleBtn.querySelector("i").className = "fas fa-sun";
      }
  }

  // Send message function
  function sendMessage() {
      const message = chatInput.value.trim();

      if (message !== "") {
          // Add user message to chat
          addMessageToChat("user", message);

          // Clear input
          chatInput.value = "";

          // Show typing indicator
          showTypingIndicator();

          // Play sound
          playSound("message-sound");

          // Simulate bot response after delay
          setTimeout(() => {
              // Hide typing indicator
              hideTypingIndicator();

              // Get bot response
              const botResponse = getBotResponse(message);

              // Add bot message to chat
              addMessageToChat("bot", botResponse);

              // Play notification sound
              playSound("notification-sound");
          }, 1500);
      } else {
          showToast("Please enter a message", "warning");
      }
  }

  // Add message to chat
  function addMessageToChat(sender, message) {
      const messageElement = document.createElement("div");
      messageElement.className = `message ${sender}-message`;

      const timestamp = getCurrentTimestamp();

      if (sender === "bot") {
          messageElement.innerHTML = `
              <div class="avatar">
                  <img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/bot-avatar.jpg-ZJd6kTjzi2T9wNduoG1Mc6Gl6ykmhU.jpeg" alt="Bot Avatar">
              </div>
              <div class="message-content">
                  <p>${message}</p>
                  <span class="timestamp">${timestamp}</span>
              </div>
          `;
      } else {
          messageElement.innerHTML = `
              <div class="message-content">
                  <p>${message}</p>
                  <span class="timestamp">${timestamp}</span>
              </div>
              <div class="avatar">
                  <img src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/user-avatar.jpg-ZLgxbA78cQsPQYH1AACzexODM64bHY.jpeg" alt="User Avatar">
              </div>
          `;
      }

      chatBox.appendChild(messageElement);

      // Add ripple effect to new message
      messageElement.classList.add("new-message");
      setTimeout(() => {
          messageElement.classList.remove("new-message");
      }, 500);

      // Scroll to bottom of chat
      chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Show typing indicator
  function showTypingIndicator() {
      typingIndicator.classList.remove("hidden");
      chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Hide typing indicator
  function hideTypingIndicator() {
      typingIndicator.classList.add("hidden");
  }

  // Get bot response (mock)
  function getBotResponse(message) {
      message = message.toLowerCase();

      // Check for exact matches
      for (const key in mockBotResponses) {
          if (message.includes(key)) {
              return mockBotResponses[key];
          }
      }

      // Default response
      return mockBotResponses.default;
  }

  // Get current timestamp
  function getCurrentTimestamp() {
      const now = new Date();
      let hours = now.getHours();
      const minutes = now.getMinutes().toString().padStart(2, "0");
      const ampm = hours >= 12 ? "PM" : "AM";
      hours = hours % 12;
      hours = hours ? hours : 12; // Convert 0 to 12
      return `Today, ${hours}:${minutes} ${ampm}`;
  }

  // Speech recognition for voice input
  function setupSpeechRecognition() {
      if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
          const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
          const recognition = new SpeechRecognition();

          recognition.lang = "en-US";
          recognition.continuous = false;
          recognition.interimResults = false;

          recognition.onstart = () => {
              voiceInputBtn.classList.add("active");
              showToast("Listening...", "info");
          };

          recognition.onresult = (event) => {
              const transcript = event.results[0][0].transcript;
              chatInput.value = transcript;
              showToast("Voice captured!", "success");
          };

          recognition.onend = () => {
              voiceInputBtn.classList.remove("active");
          };

          recognition.onerror = (event) => {
              showToast("Voice recognition error: " + event.error, "error");
              voiceInputBtn.classList.remove("active");
          };

          voiceInputBtn.addEventListener("click", () => {
              recognition.start();
              playSound("message-sound");
          });
      } else {
          voiceInputBtn.style.display = "none";
          showToast("Voice recognition not supported in this browser", "warning");
      }
  }

  // Text to speech functionality
  function setupTextToSpeech() {
      if ("speechSynthesis" in window) {
          textToSpeechBtn.addEventListener("click", () => {
              // Get the last bot message
              const botMessages = document.querySelectorAll(".bot-message .message-content p");
              if (botMessages.length > 0) {
                  const lastMessage = botMessages[botMessages.length - 1].textContent;
                  speakText(lastMessage);
                  playSound("message-sound");
                  showToast("Speaking text...", "info");
              } else {
                  showToast("No message to speak", "warning");
              }
          });
      } else {
          textToSpeechBtn.style.display = "none";
          showToast("Text-to-speech not supported in this browser", "warning");
      }
  }

  // Speak text function
  function speakText(text) {
      if ("speechSynthesis" in window) {
          // Cancel any ongoing speech
          window.speechSynthesis.cancel();
          
          const utterance = new SpeechSynthesisUtterance(text);
          
          // Get available voices
          const voices = window.speechSynthesis.getVoices();
          
          // Try to find a female English voice
          const englishVoice = voices.find(voice => 
              voice.lang.includes('en') && voice.name.includes('Female')
          ) || voices.find(voice => voice.lang.includes('en')) || voices[0];
          
          if (englishVoice) {
              utterance.voice = englishVoice;
          }
          
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          
          window.speechSynthesis.speak(utterance);
      }
  }

  // Generate lesson
  function generateLesson() {
      const language = lessonLanguage.value;
      const topic = lessonTopic.value;
      const level = lessonLevel.value;

      if (!language || !topic) {
          showToast("Please select both a language and a topic!", "warning");
          return;
      }

      // Show loading animation
      const spinner = document.querySelector(".spinner");
      const btnText = document.querySelector(".btn-text");

      spinner.classList.remove("hidden");
      btnText.textContent = "Generating...";

      // Play sound
      playSound("message-sound");

      // Simulate API call with timeout
      setTimeout(() => {
          // Hide loading animation
          spinner.classList.add("hidden");
          btnText.textContent = "Generate Lesson";

          // Show lesson result
          lessonResult.classList.remove("hidden");

          // Update lesson content
          document.getElementById("lesson-title").textContent =
              `${capitalizeFirstLetter(topic)} in ${capitalizeFirstLetter(language)} (${capitalizeFirstLetter(level)})`;

          document.getElementById("lesson-content").innerHTML = generateMockLesson(language, topic, level);

          // Add flip animation to lesson card
          const lessonCard = document.querySelector(".lesson-card");
          lessonCard.style.animation = "none";
          setTimeout(() => {
              lessonCard.style.animation = "fadeIn 0.5s ease";
          }, 10);

          // Play notification sound
          playSound("notification-sound");
          
          // Show success toast
          showToast("Lesson generated successfully!", "success");

          // Scroll to lesson result
          lessonResult.scrollIntoView({ behavior: "smooth" });
      }, 2000);
  }

  // Generate mock lesson content
  function generateMockLesson(language, topic, level) {
      const lessons = {
          spanish: {
              greetings: {
                  beginner: `
                      <h4>Common Greetings</h4>
                      <ul>
                          <li><strong>Hola</strong> - Hello</li>
                          <li><strong>Buenos días</strong> - Good morning</li>
                          <li><strong>Buenas tardes</strong> - Good afternoon</li>
                          <li><strong>Buenas noches</strong> - Good evening</li>
                          <li><strong>¿Cómo estás?</strong> - How are you?</li>
                          <li><strong>Estoy bien, gracias</strong> - I'm fine, thank you</li>
                      </ul>
                      <h4>Practice Dialogue</h4>
                      <p><strong>Person A:</strong> Hola, buenos días. ¿Cómo estás?<br>
                      <strong>Person B:</strong> Hola, estoy bien, gracias. ¿Y tú?<br>
                      <strong>Person A:</strong> Muy bien, gracias.</p>
                  `,
                  intermediate: `
                      <h4>Intermediate Greetings and Introductions</h4>
                      <ul>
                          <li><strong>Encantado/a de conocerte</strong> - Pleased to meet you</li>
                          <li><strong>¿Cómo te ha ido?</strong> - How have you been?</li>
                          <li><strong>¿Qué tal tu día?</strong> - How was your day?</li>
                          <li><strong>Me llamo...</strong> - My name is...</li>
                          <li><strong>Soy de...</strong> - I'm from...</li>
                      </ul>
                      <h4>Practice Dialogue</h4>
                      <p><strong>Person A:</strong> Hola, me llamo Carlos. ¿Cómo te llamas?<br>
                      <strong>Person B:</strong> Encantada de conocerte, Carlos. Me llamo María. ¿De dónde eres?<br>
                      <strong>Person A:</strong> Soy de México. ¿Y tú?<br>
                      <strong>Person B:</strong> Soy de España. ¿Qué tal tu día?</p>
                  `,
                  advanced: `
                      <h4>Advanced Greetings and Small Talk</h4>
                      <ul>
                          <li><strong>Es un placer conocerte en persona</strong> - It's a pleasure to meet you in person</li>
                          <li><strong>¿Qué has estado haciendo últimamente?</strong> - What have you been up to lately?</li>
                          <li><strong>Me alegra verte de nuevo</strong> - I'm glad to see you again</li>
                          <li><strong>¿Cómo te va en el trabajo/los estudios?</strong> - How's work/school going?</li>
                      </ul>
                      <h4>Practice Dialogue</h4>
                      <p><strong>Person A:</strong> ¡María! Me alegra verte de nuevo. ¿Qué has estado haciendo últimamente?<br>
                      <strong>Person B:</strong> ¡Carlos! Igualmente. He estado muy ocupada con mi nuevo trabajo. ¿Y tú? ¿Cómo te va en los estudios?<br>
                      <strong>Person A:</strong> Me va bastante bien, gracias. Estoy a punto de terminar mi maestría en economía. ¿Te gustaría tomar un café y ponernos al día?</p>
                  `,
              },
              food: {
                  beginner: `
                      <h4>Basic Food Vocabulary</h4>
                      <ul>
                          <li><strong>La comida</strong> - Food</li>
                          <li><strong>El desayuno</strong> - Breakfast</li>
                          <li><strong>El almuerzo</strong> - Lunch</li>
                          <li><strong>La cena</strong> - Dinner</li>
                          <li><strong>El agua</strong> - Water</li>
                          <li><strong>El pan</strong> - Bread</li>
                      </ul>
                      <h4>Useful Phrases</h4>
                      <ul>
                          <li><strong>Tengo hambre</strong> - I'm hungry</li>
                          <li><strong>Tengo sed</strong> - I'm thirsty</li>
                          <li><strong>¿Dónde está el restaurante?</strong> - Where is the restaurant?</li>
                      </ul>
                  `,
              },
          },
          french: {
              greetings: {
                  beginner: `
                      <h4>Common Greetings</h4>
                      <ul>
                          <li><strong>Bonjour</strong> - Hello/Good day</li>
                          <li><strong>Salut</strong> - Hi (informal)</li>
                          <li><strong>Bonsoir</strong> - Good evening</li>
                          <li><strong>Comment allez-vous?</strong> - How are you? (formal)</li>
                          <li><strong>Comment ça va?</strong> - How are you? (informal)</li>
                          <li><strong>Je vais bien, merci</strong> - I'm fine, thank you</li>
                      </ul>
                  `,
              },
          },
      };

      // Return lesson content if available, otherwise return a default message
      if (lessons[language] && lessons[language][topic] && lessons[language][topic][level]) {
          return lessons[language][topic][level];
      } else {
          return `
              <p>This is a custom ${level} lesson about ${topic} in ${language}.</p>
              <p>The lesson would include vocabulary, grammar points, and practice exercises tailored to your level.</p>
              <p>Try different combinations of languages, topics, and levels to see more sample content!</p>
          `;
      }
  }

  // Speak lesson content
  function speakLesson() {
      const lessonContent = document.getElementById("lesson-content").textContent;
      speakText(lessonContent);
      playSound("message-sound");
      showToast("Speaking lesson content...", "info");
  }

  // Save lesson (mock functionality)
  function saveLesson() {
      showToast("Lesson saved to your account!", "success");
      playSound("notification-sound");
  }

  // Share lesson (mock functionality)
  function shareLesson() {
      const shareOptions = document.createElement("div");
      shareOptions.className = "share-options";
      shareOptions.innerHTML = `
          <div class="share-overlay">
              <div class="share-modal">
                  <h4>Share Lesson</h4>
                  <div class="share-buttons">
                      <button class="share-btn facebook">
                          <i class="fab fa-facebook-f"></i> Facebook
                      </button>
                      <button class="share-btn twitter">
                          <i class="fab fa-twitter"></i> Twitter
                      </button>
                      <button class="share-btn whatsapp">
                          <i class="fab fa-whatsapp"></i> WhatsApp
                      </button>
                      <button class="share-btn email">
                          <i class="fas fa-envelope"></i> Email
                      </button>
                  </div>
                  <button class="close-share">Close</button>
              </div>
          </div>
      `;

      document.body.appendChild(shareOptions);

      // Add event listeners to share buttons
      shareOptions.querySelectorAll('.share-btn').forEach(btn => {
          btn.addEventListener('click', function() {
              const platform = this.classList[1];
              showToast(`Sharing to ${platform}...`, "success");
              setTimeout(() => {
                  document.body.removeChild(shareOptions);
              }, 1000);
          });
      });

      // Close share modal
      const closeBtn = document.querySelector(".close-share");
      closeBtn.addEventListener("click", () => {
          document.body.removeChild(shareOptions);
      });

      playSound("notification-sound");
  }

  // Helper function to capitalize first letter
  function capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
  }

  // Play UI sounds
  function playSound(soundId) {
      const sound = document.getElementById(soundId);
      if (sound) {
          sound.currentTime = 0;
          sound.play().catch(err => {
              console.log("Audio playback error:", err);
          });
      }
  }
  
  // Show toast notification
  function showToast(message, type = "info") {
      const toast = document.createElement("div");
      toast.className = `toast ${type}`;
      
      let icon = "fa-info-circle";
      if (type === "success") icon = "fa-check-circle";
      if (type === "warning") icon = "fa-exclamation-triangle";
      if (type === "error") icon = "fa-times-circle";
      
      toast.innerHTML = `
          <i class="fas ${icon}"></i>
          <span>${message}</span>
      `;
      
      toastContainer.appendChild(toast);
      
      // Remove toast after 3 seconds
      setTimeout(() => {
          if (toast.parentNode === toastContainer) {
              toastContainer.removeChild(toast);
          }
      }, 3000);
  }

  // Initialize the app
  init();
});