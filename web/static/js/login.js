document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#switchReg').addEventListener('click', () => {
        document.querySelector('#login-div').style.display = 'none';
        document.querySelector('#register-div').style.display = 'flex';
    })
    document.querySelector('#switchLogin').addEventListener('click', () => {
        document.querySelector('#register-div').style.display = 'none';
        document.querySelector('#login-div').style.display = 'flex';
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