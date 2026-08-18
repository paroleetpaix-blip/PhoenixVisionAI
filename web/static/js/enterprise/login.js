/*
========================================================
PHOENIX VISION AI
Enterprise Login
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "login-form"
            );


        const username =
            document.getElementById(
                "username"
            );


        const password =
            document.getElementById(
                "password"
            );


        const loginButton =
            document.getElementById(
                "login-button"
            );


        const errorBox =
            document.getElementById(
                "login-error"
            );


        const togglePassword =
            document.getElementById(
                "toggle-password"
            );


        togglePassword.addEventListener(
            "click",
            () => {

                password.type =
                    password.type ===
                    "password"
                    ?
                    "text"
                    :
                    "password";

            }
        );


        form.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                errorBox.textContent =
                    "";


                const user =
                    username.value.trim();


                const pass =
                    password.value;


                if(!user){

                    errorBox.textContent =
                        "Veuillez entrer votre identifiant.";

                    username.focus();

                    return;

                }


                if(!pass){

                    errorBox.textContent =
                        "Veuillez entrer votre mot de passe.";

                    password.focus();

                    return;

                }


                loginButton.disabled =
                    true;


                loginButton.textContent =
                    "Connexion...";


                try{

                    const formData =
                        new FormData();


                    formData.append(
                        "username",
                        user
                    );


                    formData.append(
                        "password",
                        pass
                    );


                    const response =
                        await fetch(
                            "/api/login",
                            {

                                method:"POST",

                                body:formData,

                                credentials:
                                    "same-origin"

                            }
                        );


                    const data =
                        await response.json();


                    if(
                        !response.ok
                        ||
                        !data.success
                    ){

                        errorBox.textContent =
                            data.message
                            ||
                            "Identifiants incorrects.";


                        loginButton.disabled =
                            false;


                        loginButton.textContent =
                            "Se connecter";


                        return;

                    }


                    if(data.username){

                        localStorage.setItem(
                            "phoenix_user",
                            data.username
                        );

                    }


                    if(data.role){

                        localStorage.setItem(
                            "phoenix_role",
                            data.role
                        );

                    }


                    loginButton.textContent =
                        "Accès autorisé";


                    window.setTimeout(
                        () => {

                            if(
                                data.must_change_password
                                ===
                                true
                            ){

                                window.location.replace(
                                    "/enterprise"
                                );

                                return;
                            }

                             window.location.replace(
                                "/enterprise"
                            );

                        },

                        300
                    );

                }

                catch(error){

                    console.error(
                        error
                    );


                    errorBox.textContent =
                        "Impossible de contacter Phoenix Server.";


                    loginButton.disabled =
                        false;


                    loginButton.textContent =
                        "Se connecter";

                }

            }
        );

    }
);
