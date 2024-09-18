// global varibales
let user = null;
let benhan = null;
let currentBenhan = null;

// handle drawing recogRes
function displayResults(filename, segments) {
  const result = document.querySelector(".result");

  const resultContainer = document.querySelector(".result > .container");
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
}

// hanlde benhan
const handleBenhAn = (benhanIndex) => {
  currentBenhan = benhan[benhanIndex][Object.keys(benhan[benhanIndex])[0]];
  console.log(currentBenhan);
  // reset
  document.querySelector(
    ".modal-content"
  ).innerHTML = `<span class="close">x</span>
        <p>Kê đơn thuốc</p>
        <div class="result" style="display: flex">
          <h2 style="align-self: flex-start; margin-left: 1rem">
            Kết quả nhận diện
          </h2>
          <div class="container">s</div>
        </div>
        <div class="medicinelist">
          <h2 style="align-self: flex-start; margin-left: 1rem">
            Kê đơn thuốc
          </h2>
          <div>
            <textarea name="text" cols="40" rows="5" id="pillist" style="margin: 1rem 2rem; margin-bottom: .25rem"></textarea>
          </div>
          <div class="action">
              <button onclick="handlePostPrescription()">Hoàn tất</button>
          </div>
        </div>
      </div>`;
  showpopup();
  displayResults(
    currentBenhan.recogSessionData.originalImage,
    currentBenhan.recogSessionData.recog
  );
};

const handlePostPrescription = () => {
  let pillist = document.querySelector("#pillist").value;
  fetch('/createPrescription', {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      "pillList": pillist,
      "userID": currentBenhan.recogSessionData.userID
    })
  })
  .then(req => {return req.json()})
  .then(res => {
    if (res.status == "true") alert("Tạo đơn thuốc thành công");
  })
};

document.addEventListener("DOMContentLoaded", () => {
  fetch("/DocHome", {
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

  // get benhan
  fetch("/getBenhAn")
    .then((req) => {
      return req.json();
    })
    .then((res) => {
      benhan = res;
    })
    .then(() => {
      // display benhan
      const container = document.querySelector(".pending");
      for (let i in benhan) {
        const benhandetail = benhan[i][Object.keys(benhan[i])[0]];
        const datetime = new Date(benhandetail.recogSessionData.timestamp);
        const elem = `<div class="item" onclick="handleBenhAn(${i})">
              <div class="image">
                <img src="/images/${
                  benhandetail.recogSessionData.originalImage
                }" alt="">
              </div>
              <div class="text">
                <p>${datetime.getDate()}/${datetime.getMonth()}/${datetime.getFullYear()}</p>
                <p>${datetime.getHours()}:${datetime.getMinutes()}</p>
              </div>
            </div>`;
        container.innerHTML += elem;
      }
    });
});

function getData(table, format) {
  var rows = table.tBodies[0].rows,
    header_row = rows[0],
    result = [],
    header = [],
    format =
      format ||
      function (val) {
        return val;
      },
    i,
    j,
    cell,
    row,
    row_data;

  // extract header
  for (i = 0, l = header_row.cells.length; i < l; i++) {
    cell = header_row.cells[i];
    header.push(cell.textContent || cell.innerText);
  }

  // extract values
  for (i = 1, l = rows.length; i < l; i++) {
    row = rows[i];
    row_data = {};
    for (j = 0, l = row.cells.length; j < l; j++) {
      cell = row.cells[j];
      row_data[header[j]] = format(i, j, cell.textContent || cell.innerText);
    }
    result.push(row_data);
  }
  return result;
}
