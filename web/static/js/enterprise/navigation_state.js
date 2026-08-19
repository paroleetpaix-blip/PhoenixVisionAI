/*
========================================================
PHOENIX VISION AI
Enterprise Navigation State
v4.4.2
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const navigationItems =
            Array.from(
                document.querySelectorAll(
                    ".sidebar-item, .console-nav-item"
                )
            );


        function normalizePath(
            value
        ) {

            if(!value){

                return "/";
            }


            if(
                value.length > 1
                &&
                value.endsWith("/")
            ){

                return value.slice(
                    0,
                    -1
                );

            }


            return value;

        }


        /*
        ====================================================
        PAGE ACTIVE
        ====================================================
        */

        const currentPath =
            normalizePath(
                window.location.pathname
            );


        navigationItems.forEach(
            item => {

                const rawHref =
                    item.getAttribute(
                        "href"
                    );


                if(
                    !rawHref
                    ||
                    rawHref.startsWith("#")
                ){

                    return;

                }


                let targetPath;


                try{

                    targetPath =
                        normalizePath(
                            new URL(
                                rawHref,
                                window.location.origin
                            ).pathname
                        );

                }
                catch{

                    return;

                }


                const isActive =
                    targetPath === currentPath;


                item.classList.toggle(
                    "active",
                    isActive
                );


                if(isActive){

                    item.setAttribute(
                        "aria-current",
                        "page"
                    );

                }
                else{

                    item.removeAttribute(
                        "aria-current"
                    );

                }

            }
        );


        /*
        ====================================================
        BADGES ALERTES
        ====================================================
        */

        function getAlertBadges(){

            const alertLinks =
                Array.from(
                    document.querySelectorAll(
                        'a[href="/alerts"]'
                    )
                );


            return alertLinks.map(
                link => {

                    let badge =
                        link.querySelector(
                            ".menu-badge, .live-alert-badge"
                        );


                    if(!badge){

                        badge =
                            document.createElement(
                                "span"
                            );

                        badge.className =
                            "live-alert-badge";

                        link.appendChild(
                            badge
                        );

                    }


                    /*
                    Toujours invisible AVANT
                    d'avoir reçu la réponse API.
                    */

                    badge.classList.remove(
                        "alert-badge-visible"
                    );

                    badge.classList.add(
                        "alert-badge-hidden"
                    );

                    badge.setAttribute(
                        "aria-hidden",
                        "true"
                    );


                    return badge;

                }
            );

        }


        const alertBadges =
            getAlertBadges();


        function hideAlertBadges(){

            alertBadges.forEach(
                badge => {

                    badge.classList.remove(
                        "alert-badge-visible"
                    );

                    badge.classList.add(
                        "alert-badge-hidden"
                    );

                    badge.setAttribute(
                        "aria-hidden",
                        "true"
                    );

                }
            );

        }


        function showAlertBadges(
            count
        ){

            alertBadges.forEach(
                badge => {

                    badge.textContent =
                        count > 99
                        ?
                        "99+"
                        :
                        String(
                            count
                        );


                    badge.classList.remove(
                        "alert-badge-hidden"
                    );

                    badge.classList.add(
                        "alert-badge-visible"
                    );


                    badge.setAttribute(
                        "aria-hidden",
                        "false"
                    );


                    badge.title =
                        count === 1
                        ?
                        "1 alerte ouverte"
                        :
                        `${count} alertes ouvertes`;

                }
            );

        }


        async function updateAlertBadges(){

            if(
                alertBadges.length === 0
            ){

                return;

            }


            try{

                const response =
                    await fetch(
                        "/api/alerts?limit=1",
                        {
                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
                        }
                    );


                if(!response.ok){

                    hideAlertBadges();

                    return;

                }


                const data =
                    await response.json();


                if(
                    data.success !== true
                ){

                    hideAlertBadges();

                    return;

                }


                const openCount =
                    Number(
                        data.open
                    ) || 0;


                if(openCount <= 0){

                    hideAlertBadges();

                    return;

                }


                showAlertBadges(
                    openCount
                );

            }
            catch{

                /*
                En cas d'erreur API,
                aucun faux voyant rouge.
                */

                hideAlertBadges();

            }

        }


        updateAlertBadges();


        window.setInterval(
            updateAlertBadges,
            10000
        );

    }
);
