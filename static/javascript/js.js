const password = document.getElementById("password");
const eyetoggle = document.getElementById("eyepassword");
const icon = eyetoggle.querySelector("i");

eyetoggle.addEventListener("click", function () {
    if (password.type === "password") {
        password.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        password.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
})

let time = 120;
const countdown = document.getElementById("countdown");
if (countdown) {
    const timer = setInterval(function () {
        let minutes = Math.floor(time / 60);
        let seconds = time % 60;
        countdown.innerHTML =
            String(minutes).padStart(2, "0")
            + ":" +
            String(seconds).padStart(2, "0");

        if (time <= 0) {
            clearInterval(timer);
            countdown.innerHTML = "Expired";
        }
        time--;
    }, 1000);
}

document.addEventListener("DOMContentLoaded", function () {
    const mobileMenuToggle = document.querySelector(".mobile-menu-toggle");
    const navMenu = document.querySelector(".nav-menu");

    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener("click", function () {
            const expanded = this.getAttribute("aria-expanded") === "true";
            this.setAttribute("aria-expanded", String(!expanded));
            navMenu.classList.toggle("active");
        });
    }

    const submenuItems = document.querySelectorAll(".nav-menu li");
    submenuItems.forEach((item) => {
        const toggle = item.querySelector(".submenu-toggle");
        const submenu = item.querySelector(":scope > ul");
        const link = item.querySelector(":scope > a.nav-link");

        function toggleSubmenu(event) {
            event.preventDefault();
            event.stopPropagation();
            if (!submenu) return;
            submenu.classList.toggle("active");
            const icon = toggle?.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-chevron-down");
                icon.classList.toggle("fa-chevron-up");
            }
        }

        if (toggle) {
            toggle.addEventListener("click", toggleSubmenu);
        }

        if (link && submenu) {
            link.addEventListener("click", function (event) {
                if (window.innerWidth < 768) {
                    toggleSubmenu(event);
                }
            });
        }
    });
});