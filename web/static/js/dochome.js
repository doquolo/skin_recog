// global varibales
let user = null;
let benhan = null;

// hanlde benhan
const handleBenhAn = (benhanIndex) => {
    console.log(benhan[benhanIndex])
}

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
        fetch('/getBenhAn')
        .then(req => {return req.json()})
        .then(res => {
            benhan = res;
        })
        .then(() => {
            // display benhan 
            const container = document.querySelector('.pending')
            for (let i in benhan) {
                const benhandetail =  benhan[i][Object.keys(benhan[i])[0]];
                const datetime = new Date(benhandetail.recogSessionData.timestamp);
                const elem = `<div class="item" onclick="handleBenhAn(${i})">
              <div class="image">
                <img src="/images/${benhandetail.recogSessionData.originalImage}" alt="">
              </div>
              <div class="text">
                <p>${datetime.getDate()}/${datetime.getMonth()}/${datetime.getFullYear()}</p>
                <p>${datetime.getHours()}:${datetime.getMinutes()}</p>
              </div>
            </div>`
                container.innerHTML += elem;
            }
        })

});
