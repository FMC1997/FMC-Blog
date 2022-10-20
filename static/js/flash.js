function delete_message_sucesso() {
  document.querySelector('.Alerta_sucesso').style.display = 'none';
}

function delete_message_erro() {
  document.querySelector('.Alerta_erro').style.display = 'none';
}

//Faz desaparecer as mensagens de sucesso depois de 7s

let Alerta = document.getElementsByClassName("Alerta_sucesso")
for (let elemento = 0; elemento < Alerta.length; elemento++)
  setTimeout(
    delete_message_sucesso(), 6000);

let loader = document.getElementById("loadingScreen")
window.addEventListener("load", function () {
  loader.style.display = "none";
})