    document.addEventListener("DOMContentLoaded", () => {


        const swiper = new Swiper('.swiper-initial', {
            // Optional parameters
            loop: true,
            slidesPerView: 1,

            pagination: {
                el: '.swiper-pagination',
            },

            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },

            // And if we need scrollbar
            scrollbar: {
                el: '.swiper-scrollbar',
            },
        });


        // console.log("done");

    })
