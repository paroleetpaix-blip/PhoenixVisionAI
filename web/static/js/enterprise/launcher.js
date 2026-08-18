/*
========================================================
PHOENIX VISION AI
Launcher Enterprise
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const panel =
            document.getElementById(
                "boot-status"
            );


        const items =
            Array.from(
                document.querySelectorAll(
                    ".boot-item"
                )
            );


        const message =
            document.getElementById(
                "boot-message"
            );


        const launcher =
            document.querySelector(
                ".launcher"
            );


        const stages = [

            "Vérification du processeur...",

            "Analyse de la mémoire...",

            "Initialisation GPU...",

            "Chargement OpenCV...",

            "Vérification des caméras...",

            "Connexion à la base de données...",

            "Vérification réseau...",

            "Validation des permissions..."

        ];


        let index = 0;


        function verifyNext(){

            if(
                index >=
                items.length
            ){

                message.textContent =
                    "Système opérationnel.";


                /*
                Lorsque tous les composants
                sont verts :

                attendre 5 secondes,
                puis masquer la liste.
                */

                window.setTimeout(
                    () => {

                        panel.classList.add(
                            "hidden"
                        );

                    },

                    5000
                );


                /*
                15 secondes APRÈS
                la disparition du panneau.

                Donc :
                5 sec + 15 sec = 20 sec
                après la fin des contrôles.
                */

                window.setTimeout(
                    () => {

                        launcher.classList.add(
                            "fade-out"
                        );


                        window.setTimeout(
                            () => {

                                window.location.replace(
                                    "/login"
                                );

                            },

                            1000
                        );

                    },

                    7000
                );


                return;

            }


            message.textContent =
                stages[index];


            items[index]
                .classList
                .add(
                    "active"
                );


            index++;


            window.setTimeout(
                verifyNext,
                600
            );

        }


        window.setTimeout(
            verifyNext,
            650
        );

    }
);