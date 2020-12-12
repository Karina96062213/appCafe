function validar_formulario()
{
    var usuario = document.formularioRegistro.nuser;
    var correo = document.formularioRegistro.euser;
    var clave = document.formularioRegistro.cuser;
     
    var usuario_len = usuario.value.length;
    if(usuario_len == 0 || usuario_len < 8)
    {
       alert("Debes ingresar un usuario con mínimo 8 caracteres");
       usuario.focus();
       //return false; //Para la parte dos, que los datos se conserven
    }
    
    var formatoCorreo = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if(!correo.value.match(formatoCorreo))
    {
       alert("Debes ingresar un correo electrónico valido");
       correo.focus();
       //return false; //Para la parte dos, que los datos se conserven
    }
    
    var clave_len = clave.value.length;
    if (clave_len == 0 || clave_len < 8)
    {
       alert("Debes ingresar una clave con más de 8 caracteres");
       clave.focus();
    }
}