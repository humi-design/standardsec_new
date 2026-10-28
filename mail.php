<?php

$name = $_POST["name"];
$email = $_POST["email"];
$message = $_POST["message"];

require "vendor/autoload.php";

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;

$mail = new PHPMailer(true);

// $mail->SMTPDebug = SMTP::DEBUG_SERVER;

$mail->isSMTP();
$mail->SMTPAuth = true;

$mail->Host = "premium86.web-hosting.com";
$mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
$mail->Port = 465;

$mail->Username = "somil@humisense.com";
$mail->Password = "Kalpana@gmail.com";

$mail->setFrom($email, $name);
$mail->addAddress("dave@example.com", "Dave");

$mail->Subject = $subject;
$mail->Body = $message;

$mail->send();

header("Location: sent.html");