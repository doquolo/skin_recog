document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#switchReg').addEventListener('click', () => {
        document.querySelector('#login-div').style.display = 'none';
        document.querySelector('#register-div').style.display = 'flex';
    })
    document.querySelector('#switchLogin').addEventListener('click', () => {
        document.querySelector('#register-div').style.display = 'none';
        document.querySelector('#login-div').style.display = 'flex';
    })
    document.querySelector("#login").addEventListener('click', () => {
        const username = document.querySelector("#username-login").value;
        const password = document.querySelector("#password-login").value;

        if (username == "" || password == "") {
            alert("Các ô dữ liệu không được để trống!");
        } else {
            fetch('/login', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    action: "login",
                    username: username,
                    password: password
                })
            })
            .then(req => {return req.json()})
            .then(res => {
                if (res.status == "true") {
                    setCookie("sessionID", String(res.data.sessionID), 30); // create sessionID that exprired after 15m
                    location.replace('/');
                }
                else alert("Tên đăng nhập hoặc mật khẩu không đúng!");
            })
        }
    })
    document.querySelector("#register").addEventListener('click', () => {
        const name = document.querySelector("#name-register").value;
        const username = document.querySelector("#username-register").value;
        const password = document.querySelector("#password-register").value;
        const role = document.querySelector('#role').value

        if (username == "" || password == "" || name == "") {
            alert("Các ô dữ liệu không được để trống!");
        } else {
            fetch('/login', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    action: "register",
                    name: name,
                    username: username,
                    password: password,
                    role: role
                })
            })
            .then(req => {return req.json()})
            .then(res => {
                if (res.status == "true") {
                    alert("Tạo tài khoản thành công!");
                    location.reload();
                }
            })
        }   
    })
})