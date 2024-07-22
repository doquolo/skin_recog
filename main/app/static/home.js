window.addEventListener("DOMContentLoaded", (event) => {
  const uploadInput = document.getElementById("upload-input");
  const preview = document.getElementById("preview");
  const useButton = document.getElementById("use-button");

  let uploadedFilename = "";

  // My form
  document.getElementById("myForm").addEventListener("use-button", function (e) {
      e.preventDefault(); // Prevent form submission
  });


  function handleImageUpload() {
      const file = uploadInput.files[0];
      if (file) {
          const reader = new FileReader();
          reader.onload = function (e) {
              const image = new Image();
              image.src = e.target.result;
              image.style.width = "100%";
              image.style.height = "100%";
              image.style.objectFit = "contain";
              preview.innerHTML = "";
              preview.appendChild(image);
          };
          reader.readAsDataURL(file);
      }
      //alert("hello");
  }

  async function handleUseButtonClick() {
      const file = uploadInput.files[0];
      if (file) {
          const formData = new FormData();
          formData.append("image", file);

          try {
              const response = await fetch("/save-image", {
                  method: "POST",
                  body: formData
              });
              const result = await response.json();
              uploadedFilename = result.filename;

              alert("Vui lòng chờ \nQuá trình này có thể mất nhiều thời gian");
              // start loading animation
              document.querySelector("#loading-overlay").style.display = "flex";
              document.body.classList.add("loading");

              performSkinRecognition();
          } catch (error) {
              console.error("Error saving image:", error);
          }
      }
  }

  async function performSkinRecognition() {

      // get choices
      var checkboxes = document.querySelectorAll('[name="problem"]');
      var selectedChoicesSet = new Set();

      checkboxes.forEach(function (checkbox) {
        if (checkbox.checked) {
            selectedChoicesSet.add(checkbox.value);
        }
      });

      
      let selectedChoice = Array.from(selectedChoicesSet); // Convert set to array

      // continue with normal stuff
      const formData = new FormData();
      formData.append("filename", uploadedFilename);
      formData.append("sel", selectedChoice)

      try {
          const response = await fetch("/perform-skin-recognition", {
              method: "POST",
              body: formData
          });
          const segments = await response.json();
          displayResults(uploadedFilename, segments);
      } catch (error) {
          console.error("Error performing skin recognition:", error);
      }
  }

  function displayResults(filename, segments) {
    // remove loading animation
    document.querySelector("#loading-overlay").style.display = "none";
    document.body.classList.remove("loading");

    const result = document.querySelector(".result");
    result.classList.add("result");
    result.style.display = "flex";

    const resultContainer = document.querySelector(".container");
    resultContainer.classList.add("container");

    // Clear all existing elements in resultContainer
    resultContainer.innerHTML = '';

    // Hiển thị ảnh mới nhất trong folder test
    const testImageDiv = document.createElement("div");
    testImageDiv.classList.add("frame");

    const testImg = new Image();
    testImg.src = `/images/${filename}`;
    testImg.classList.add("frame-img");

    testImageDiv.appendChild(testImg);
    resultContainer.appendChild(testImageDiv);

    // Hiển thị các ảnh phân đoạn trong folder segments
    segments.forEach(segment => {
        const segmentDiv = document.createElement("div");
        segmentDiv.classList.add("frame-sm");

        const segmentImg = new Image();
        segmentImg.src = `/images/${filename.split('.')[0]}/${segment.image}`;
        segmentImg.classList.add("frame-sm-img");

        const info = document.createElement("p1");
        info.innerHTML = `${segment.prediction}`;
        info.classList.add("p1");
        const confidence = document.createElement("p2");
        confidence.innerHTML = `Chính xác: ${segment.confidence}%`;
        confidence.classList.add("p2");

        segmentDiv.appendChild(segmentImg);
        segmentDiv.appendChild(info);
        segmentDiv.appendChild(confidence);
        resultContainer.appendChild(segmentDiv);
    });
  }
 

  uploadInput.addEventListener("change", handleImageUpload);
  useButton.addEventListener("click", handleUseButtonClick);
});


// Chat box
document.addEventListener("DOMContentLoaded", function () {
  const chatCircle = document.getElementById("chat-icon");
  const chatBox = document.getElementById("chat-box");
  const closeButton = document.getElementById("close-button");
  const chatContent = document.getElementById("chat-content");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");

  let isOpen = false;

  function toggleChatBox() {
    isOpen = !isOpen;
    chatBox.style.display = isOpen ? "block" : "none";
    overlay.style.display = isOpen ? "block" : "none";
  }

  overlay.addEventListener('click', function() {
    content.style.display = 'none';
    overlay.style.display = 'none';
  });

  closeButton.addEventListener('click', function() {
    content.style.display = 'none';
    overlay.style.display = 'none';
  });

  function closeChatBox() {
    isOpen = false;
    chatBox.style.display = "none";
    overlay.style.display = 'none';
  }

  function appendMessage(sender, message, isTitle = false) {
    const messageElement = document.createElement("div");

    // Split the message by new lines and add <br/> tags
    const messageParts = message.split("\n");
    const formattedMessage = messageParts.join("<br/>");

    if (isTitle) {
      messageElement.innerHTML = `<strong style="color: #e9a084">${sender}:</strong><br/>${message}`;
    } else {
      // Append a line break at the end of the formatted message
      messageElement.innerHTML = `<strong>${sender}:</strong> ${formattedMessage}<br/>`;
    }

    chatContent.appendChild(messageElement);
    chatContent.scrollTop = chatContent.scrollHeight;
  }

  function sendMessage() {
    const userMessage = userInput.value.trim();
    if (userMessage !== "") {
      // Thay vì sử dụng formattedUserMessage, hãy truyền userMessage trực tiếp
      appendMessage("Bạn", userMessage);

      // Call your backend API to get the bot's response
      // Example: You can use the Fetch API or an AJAX library
      // Replace the URL with your actual backend endpoint
      let xhr = new XMLHttpRequest();
      xhr.open("POST", "/askGPT");
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("Content-Type", "application/json");

      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          console.log(xhr.status);
          // console.log(xhr.responseText);

          // Append chatbot's response with a line break
          appendMessage("Tư vấn", JSON.parse(xhr.responseText).content + "\n");
        }
      };

      xhr.send(JSON.stringify({ message: userMessage }));

      userInput.value = "";
    }
  }

  chatCircle.addEventListener("click", toggleChatBox);
  closeButton.addEventListener("click", closeChatBox);
  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
});