<?php
//include('php/header.php');

use PHPMailer\PHPMailer\PHPMailer;
require_once "PHPMailer/PHPMailer";
require_once "PHPMailer/SMTP";
require_once "PHPMailer/Exception";


$check="SELECT * FROM unitel_code_2 WHERE local ='Kwanza Norte'";
$sett = $conexao->query($check);

while($d=mysqli_fetch_array($sett)) {

    $nome = $d['encarregado'];
    $email = $d['email'];
    $hora = $d['hora'];
    


$mail = new PHPMailer();


$subject = "UNITEL CODE ROBOTICA - SELECIONADO";


$body = "
<center style='background: #E1E0E052; width: 100%'>
    <div style='padding: 1rem 2rem; background: rgba(255, 214, 184, 0.409); max-height: 1200px; max-width: 700px'>
        <br>
        <br>
        <img src='https://raw.githubusercontent.com/Katumbela/arotec2/main/imagens/email-job.webp' style='border-radius: 100px; border: 4px solid #ff680a' height='110em' alt=''>
        <br>
        <h1 style='color: #ff680a'>UNITEL CODE ROBOTICA</h1>
        <h4 style='color: #0066BE'>SELECIONADO</h4>
            <div style='text-align: start'>

        <p style='text-align: start; color:rgb(83, 83, 83); '>
            Cordiais saudações Prezado/a <b>{$nome}</b> <br>
            <span>Primeiramente pedimos desculpas pelo atrazo com a informação!</span><br>
            <br>
Informamos que o seu educando foi selecionado para participar da formação de programação e Robótica do Programa Unitel code. A mesma irá decorrer em <b>Ndalatando</b>, Rua da Missão na  <b>Escola Marista</b>, e terá início no dia 08 do mês em curso, com duração de 3 dias, de 08 - 10.
        </p>
        <p>
         
            <br>
A formação irá decorrer no período   <b> {$hora} </b><br>
    <br>
    <span style='color: rgb(0, 0, 0)'><b>Att:</b></span>
    <span style='color: rgb(121, 121, 121);'><br>

        <b style='color: black'>1. </b> O(A) Sr(a) <b>".explode(" ",$nome)[0]."</b> deverá acompanhar o seu educando no local de formação e levar consigo os Documentos de identificação. <br><br>
       
    </span>
    
            
        </p>

            </div>
        <br>
        <span style='color:rgba(105, 89, 71, 0.791); font-size: 12px'>
            Contactos: 938 811 659 &middot; unitelcode@aro-tec.net
        </span>
    </div>
    <div style='padding: 1rem 2rem; gap: 5px; background: #ff680a; max-height: 1200px; max-width: 700px'>
        
        <img src='https://github.com/Katumbela/arotec2/blob/main/imagens/logo.png?raw=true' style='height: 1.5em' alt=''>
        <br>
        <span style='font-size: 11px; color:rgb(231, 231, 231); margin-top: 1rem;'>&copy; Copyright &middot; 2023</span>
    </div>
</center>
";

//SMTP Settings
$mail->isSMTP();
$mail->Host = "smtp.gmail.com";
$mail->SMTPAuth = true;
$mail->Username = "arotec.unitelcode@gmail.com";
$mail->Password ='kpputtdjtcjqmjvo';
$mail->Port = 465; //587
$mail->SMTPSecure = "ssl"; //tls

//Email Settings
$mail->isHTML(true);
$mail->setFrom("unitelcode@aro-tec.net", " SELECIONADO - UNITEL CODE");
    
$mail->Subject = $subject;
$mail->Body = $body;

    $mail->AddAddress($email, $nome);
    
    $mail->send();

    $mail->ClearAddresses();

     echo json_encode("Email sent successfuly !");


}

?>




