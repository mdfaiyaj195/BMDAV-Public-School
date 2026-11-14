document.addEventListener("DOMContentLoaded", function () {
    let allCoursesBtn = document.getElementById("allCoursesBtn");
    let dropdownMenu = document.querySelector(".dropdown-menu");

    allCoursesBtn.addEventListener("mouseover", function () {
        dropdownMenu.style.display = "block";
    });

    dropdownMenu.addEventListener("mouseleave", function () {
        dropdownMenu.style.display = "none";
    });

    let carouselElement = document.querySelector("#carouselExample");
    
    if (carouselElement) {
        let carousel = new bootstrap.Carousel(carouselElement, {
            interval: 2000, 
            ride: "carousel",
            pause: "hover", 
            wrap: true
        });
    }

});
