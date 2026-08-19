document.addEventListener(
    "DOMContentLoaded",
    () => {

        const list =
            document.getElementById(
                "history-list"
            );

        if(!list) {
            return;
        }


        function makeButton(
            text,
            className,
            disabled=false
        ) {

            const button =
                document.createElement(
                    "button"
                );

            button.type = "button";

            button.className =
                "history-action-button "
                +
                className;

            button.disabled =
                disabled;

            button.textContent =
                text;

            return button;
        }


        function waitForHero(
            callback,
            attempt=0
        ) {

            const hero =
                document.querySelector(
                    ".history-record-hero"
                );

            if(hero) {

                callback(hero);

                return;
            }


            if(attempt < 30) {

                window.setTimeout(
                    () => {
                        waitForHero(
                            callback,
                            attempt + 1
                        );
                    },
                    50
                );
            }
        }


        function installActions(
            hero,
            record,
            permissions
        ) {

            const old =
                document.querySelector(
                    ".history-record-actions"
                );

            if(old) {
                old.remove();
            }


            const actions =
                document.createElement(
                    "section"
                );

            actions.className =
                "history-record-actions";


            if(
                permissions.history_print
                ===
                true
            ) {

                const printButton =
                    makeButton(
                        "IMPRIMER LA FICHE",
                        "primary"
                    );

                printButton.addEventListener(
                    "click",
                    () => {

                        window.open(
                            "/history/"
                            +
                            encodeURIComponent(
                                record.uuid
                            )
                            +
                            "/print",
                            "_blank",
                            "noopener,noreferrer"
                        );

                    }
                );

                actions.appendChild(
                    printButton
                );
            }


            if(
                permissions.evidence_view
                ===
                true
            ) {

                const evidence =
                    makeButton(
                        "PREUVES",
                        "",
                        true
                    );

                evidence.title =
                    "Aucune preuve média persistée";

                actions.appendChild(
                    evidence
                );
            }


            if(
                permissions.evidence_print
                ===
                true
            ) {

                const printEvidence =
                    makeButton(
                        "IMPRIMER PREUVE",
                        "",
                        true
                    );

                printEvidence.title =
                    "Aucune preuve média imprimable";

                actions.appendChild(
                    printEvidence
                );
            }


            if(
                permissions.evidence_export_video
                ===
                true
            ) {

                const video =
                    makeButton(
                        "EXPORTER VIDÉO",
                        "video",
                        true
                    );

                video.title =
                    "Aucun clip vidéo forensic associé";

                actions.appendChild(
                    video
                );
            }


            if(
                actions.children.length
                >
                0
            ) {

                hero.insertAdjacentElement(
                    "afterend",
                    actions
                );
            }
        }


        async function loadActions(
            row
        ) {

            const uuid =
                row.dataset.vehicleUuid;

            if(!uuid) {
                return;
            }


            try {

                const response =
                    await fetch(
                        "/api/history/"
                        +
                        encodeURIComponent(
                            uuid
                        ),
                        {
                            credentials:
                                "same-origin",
                            cache:
                                "no-store"
                        }
                    );


                if(!response.ok) {
                    return;
                }


                const data =
                    await response.json();


                if(
                    data.success
                    !==
                    true
                ) {
                    return;
                }


                waitForHero(
                    hero => {

                        installActions(
                            hero,
                            data.record,
                            data.permissions || {}
                        );

                    }
                );

            }
            catch(error) {

                console.error(
                    "Phoenix history actions:",
                    error
                );
            }
        }


        list.addEventListener(
            "click",
            event => {

                const row =
                    event.target.closest(
                        ".history-row"
                    );

                if(row) {
                    loadActions(row);
                }
            }
        );


        list.addEventListener(
            "keydown",
            event => {

                if(
                    event.key !== "Enter"
                    &&
                    event.key !== " "
                ) {
                    return;
                }


                const row =
                    event.target.closest(
                        ".history-row"
                    );

                if(row) {
                    loadActions(row);
                }
            }
        );

    }
);
