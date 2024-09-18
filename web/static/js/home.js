let user = null;

window.addEventListener("DOMContentLoaded", (event) => {
  document.querySelector("#prescriptions").addEventListener("click", () => {
    showpopup();
    fetch(`/getPreList?id=${user.data.userID}`)
      .then((req) => {
        return req.json();
      })
      .then((res) => {
        const listdiv = document.querySelector("#prescription-list");
        listdiv.innerHTML = "";
        for (let i in res.list) {
          const elem = `<p>Mã: ${res.list[i]}</p>`;
          console.log(elem);
          listdiv.innerHTML += elem;
        }
      });
  });

  fetch("/home", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sessionID: String(getCookie("sessionID")),
    }),
  })
    .then((res) => {
      return res.json();
    })
    .then((req) => {
      if (req.status == "false") location.replace("/login");
      console.log(req);
      user = req;
      document.querySelector(
        "#greeting"
      ).textContent = `Chào, ${user.data.name}`;
      document.querySelector(
        "#logout"
      ).href = `/logout?id=${user.data.sessionID}`;
    });

  const uploadInput = document.getElementById("upload-input");
  const preview = document.getElementById("preview");
  const useButton = document.getElementById("use-button");

  let uploadedFilename = "";

  // My form
  document
    .getElementById("myForm")
    .addEventListener("use-button", function (e) {
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
          body: formData,
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

  let recogSessionData = null;
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
    formData.append("sel", selectedChoice);

    try {
      const response = await fetch("/perform-skin-recognition", {
        method: "POST",
        body: formData,
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
    resultContainer.innerHTML = "";

    // Hiển thị ảnh mới nhất trong folder test
    const testImageDiv = document.createElement("div");
    testImageDiv.classList.add("frame");

    const testImg = new Image();
    testImg.src = `/images/${filename}`;
    testImg.classList.add("frame-img");

    testImageDiv.appendChild(testImg);
    resultContainer.appendChild(testImageDiv);

    // Hiển thị các ảnh phân đoạn trong folder segments
    segments.forEach((segment) => {
      const segmentDiv = document.createElement("div");
      segmentDiv.classList.add("frame-sm");

      const segmentImg = new Image();
      segmentImg.src = `/images/${filename.split(".")[0]}/${segment.image}`;
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

    // luu du lieu lai de su ly
    let choices = document.querySelectorAll("#myForm > form > div");
    let indications = [];
    for (let i in choices) {
      let choice = choices[i];
      if (choice.tagName == "DIV") {
        if (choice.childNodes[1].checked) {
          indications.push(choice.textContent.trim());
        }
      }
    }
    recogSessionData = {
      userID: user.data.userID,
      timestamp: Date.now(),
      recog: segments,
      originalImage: filename,
      selectedChoice: indications,
    };
    console.log(recogSessionData);
  }

  document.querySelector("#docReq").addEventListener("click", () => {
    fetch("/requestDoc", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(recogSessionData),
    })
      .then((req) => {
        return req.json();
      })
      .then((res) => {
        if (res.status == "true") {
          alert("Đã lưu yêu cầu xem xét cho bác sĩ!");
        } else {
          alert(`Đã có lỗi xảy ra :( (${res.reason})`);
        }
      });
  });

  uploadInput.addEventListener("change", handleImageUpload);
  useButton.addEventListener("click", handleUseButtonClick);
});
