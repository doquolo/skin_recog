const handleNavbar = (elem) => {
    const navbar = document.querySelector(".navbar");
    for (let i in navbar.childNodes) {
      let element = navbar.childNodes[i];
      if (element.nodeName != "#text") {
        try {
          element.classList.remove("selected");
        } catch (error) {
          console.log(error);
        }
      }
    }
    elem.classList.add("selected");
  }