/*
========================================================
PHOENIX VISION AI
First Login Password Change
========================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "change-password-form"
            );


        const currentPassword =
            document.getElementById(
                "current-password"
            );


        const newPassword =
            document.getElementById(
                "new-password"
            );


        const confirmPassword =
            document.getElementById(
                "confirm-password"
            );


        const message =
            document.getElementById(
                "password-message"
            );


        const submitButton =
            document.getElementById(
                "change-password-button"
            );


        const rules = {

            length:
                document.getElementById(
                    "rule-length"
                ),

            upper:
                document.getElementById(
                    "rule-upper"
                ),

            lower:
                document.getElementById(
                    "rule-lower"
                ),

            number:
                document.getElementById(
                    "rule-number"
                ),

            special:
                document.getElementById(
                    "rule-special"
                )

        };


        function passwordState(
            password
        ){

            return {

                length:
                    password.length >= 12,

                upper:
                    /[A-Z]/.test(
                        password
                    ),

                lower:
                    /[a-z]/.test(
                        password
                    ),

                number:
                    /\d/.test(
                        password
                    ),

                special:
                    /[^A-Za-z0-9]/.test(
                        password
                    )

            };

        }


        function updatePolicy(){

            const state =
                passwordState(
                    newPassword.value
                );


            Object.entries(
                state
            ).forEach(
                ([key, valid]) => {

                    rules[
                        key
                    ].classList.toggle(
                        "valid",
                        valid
                    );

                }
            );


            return Object.values(
                state
            ).every(Boolean);

        }


        newPassword.addEventListener(
            "input",
            updatePolicy
        );


        document
            .querySelectorAll(
                ".password-toggle"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const target =
                                document.getElementById(
                                    button.dataset.target
                                );


                            target.type =
                                target.type ===
                                "password"
                                ?
                                "text"
                                :
                                "password";

                        }
                    );

                }
            );


        form.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                message.style.color =
                    "#ff5267";


                message.textContent =
                    "";


                const oldPassword =
                    currentPassword.value;


                const password =
                    newPassword.value;


                const confirmation =
                    confirmPassword.value;


                if(!oldPassword){

                    message.textContent =
                        "Entrez votre mot de passe temporaire.";

                    return;

                }


                if(!updatePolicy()){

                    message.textContent =
                        "Le nouveau mot de passe ne respecte pas les exigences de sécurité.";

                    return;

                }


                if(
                    password
                    !==
                    confirmation
                ){

                    message.textContent =
                        "Les deux nouveaux mots de passe ne correspondent pas.";

                    return;

                }


                if(
                    password
                    ===
                    oldPassword
                ){

                    message.textContent =
                        "Le nouveau mot de passe doit être différent du mot de passe temporaire.";

                    return;

                }


                submitButton.disabled =
                    true;


                submitButton.textContent =
                    "Sécurisation du compte...";


                try{

                    const data =
                        new FormData();


                    data.append(
                        "current_password",
                        oldPassword
                    );


                    data.append(
                        "new_password",
                        password
                    );


                    data.append(
                        "confirm_password",
                        confirmation
                    );


                    const response =
                        await fetch(
                            "/api/change-password",
                            {

                                method:"POST",

                                body:data,

                                credentials:
                                    "same-origin"

                            }
                        );


                    const result =
                        await response.json();


                    if(
                        !response.ok
                        ||
                        !result.success
                    ){

                        message.textContent =
                            result.message
                            ||
                            "Le mot de passe n'a pas pu être modifié.";

                        return;

                    }


                    message.style.color =
                        "#19c577";


                    message.textContent =
                        "Mot de passe modifié. Ouverture de Phoenix Vision AI...";


                    window.setTimeout(
                        () => {

                            window.location.replace(
                                "/enterprise"
                            );

                        },

                        1100
                    );

                }

                catch(error){

                    console.error(
                        "Phoenix password:",
                        error
                    );


                    message.textContent =
                        "Impossible de contacter Phoenix Server.";

                }

                finally{

                    window.setTimeout(
                        () => {

                            submitButton.disabled =
                                false;


                            submitButton.textContent =
                                "Enregistrer mon nouveau mot de passe";

                        },

                        1300
                    );

                }

            }
        );

    }
);