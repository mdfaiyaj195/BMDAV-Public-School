document.addEventListener("DOMContentLoaded", function () {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const cards = document.querySelectorAll(
        ".home-principal-section .home-principal-card"
    );

    if (cards.length > 1 && !reducedMotion) {
        let currentCardIndex = 0;

        cards.forEach((card, index) => {
            card.hidden = index !== currentCardIndex;
        });

        window.setInterval(() => {
            cards[currentCardIndex].hidden = true;

            currentCardIndex = (currentCardIndex + 1) % cards.length;
            cards[currentCardIndex].hidden = false;
            cards[currentCardIndex].animate(
                [
                    { opacity: 0, transform: "translateX(20px)" },
                    { opacity: 1, transform: "translateX(0)" }
                ],
                { duration: 450, easing: "ease-out" }
            );
        }, 2000);
    }

    const gallery = document.querySelector(".home-gallery-grid");
    const galleryItems = gallery ? Array.from(gallery.children) : [];

    if (!gallery || galleryItems.length <= 1 || reducedMotion) {
        return;
    }

    galleryItems.slice(0, Math.min(3, galleryItems.length)).forEach((item) => {
        const clone = item.cloneNode(true);
        clone.setAttribute("aria-hidden", "true");
        clone.tabIndex = -1;
        gallery.appendChild(clone);
    });

    let currentIndex = 0;
    let autoplayTimer;
    let scrollTimer;

    const getSlideWidth = () => {
        const galleryStyle = window.getComputedStyle(gallery);
        const gap = parseFloat(galleryStyle.columnGap) || 0;
        return galleryItems[0].getBoundingClientRect().width + gap;
    };

    const startAutoplay = () => {
        if (autoplayTimer || document.hidden) {
            return;
        }

        autoplayTimer = window.setInterval(() => {
            gallery.scrollTo({
                left: (currentIndex + 1) * getSlideWidth(),
                behavior: "smooth"
            });
        }, 3500);
    };

    const stopAutoplay = () => {
        window.clearInterval(autoplayTimer);
        autoplayTimer = null;
    };

    gallery.addEventListener("scroll", () => {
        window.clearTimeout(scrollTimer);
        scrollTimer = window.setTimeout(() => {
            const slideWidth = getSlideWidth();
            const rawIndex = Math.round(gallery.scrollLeft / slideWidth);
            currentIndex = rawIndex % galleryItems.length;

            if (rawIndex >= galleryItems.length) {
                gallery.scrollLeft = currentIndex * slideWidth;
            }
        }, 120);
    });

    gallery.addEventListener("mouseenter", stopAutoplay);
    gallery.addEventListener("mouseleave", startAutoplay);
    gallery.addEventListener("focusin", stopAutoplay);
    gallery.addEventListener("focusout", (event) => {
        if (!gallery.contains(event.relatedTarget)) {
            startAutoplay();
        }
    });
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            stopAutoplay();
        } else {
            startAutoplay();
        }
    });
    window.addEventListener("resize", () => {
        gallery.scrollLeft = currentIndex * getSlideWidth();
    });

    startAutoplay();
});
