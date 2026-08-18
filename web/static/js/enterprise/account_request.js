/*
========================================================
PHOENIX VISION AI
Account Request
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "account-request-form"
            );


        const message =
            document.getElementById(
                "request-message"
            );


        const button =
            document.getElementById(
                "request-submit"
            );


        form.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                message.textContent =
                    "";


                button.disabled =
                    true;


                button.textContent =
                    "Envoi de la demande...";


                try{

                    const data =
                        new FormData(
                            form
                        );


                    const response =
                        await fetch(
                            "/api/account-request",
                            {

                                method:"POST",

                                body:data

                            }
                        );


                    const result =
                        await response.json();


                    if(
                        !response.ok
                        ||
                        !result.success
                    ){

                        message.style.color =
                            "#ff5367";


                        message.textContent =
                            result.message
                            ||
                            "La demande n'a pas pu être envoyée.";


                        return;

                    }


                    message.style.color =
                        "#16c878";


                    message.textContent =
                        "Votre demande a été envoyée. Elle sera examinée par un administrateur.";


                    form.reset();

                }

                catch(error){

                    console.error(
                        error
                    );


                    message.style.color =
                        "#ff5367";


                    message.textContent =
                        "Impossible de contacter Phoenix Server.";

                }

                finally{

                    button.disabled =
                        false;


                    button.textContent =
                        "Envoyer ma demande";

                }

            }
        );

    }
);