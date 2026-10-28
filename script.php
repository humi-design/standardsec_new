<?php 
	$to = "digitalfox.tutorials@gmail.com";
	$subject = "Thank you for your purchase";

	// In php 7.2 and newer versions we can use an array to set the headers.
	$headers = array(
		"MIME-Version" => "1.0",
		"Content-Type" =>"text/html;charset=UTF-8",
		"From" =>"dennis@mail.com",
		"Reply-To" =>"dennis@mail.com"
	);

	$name = "Dennis";

	ob_start();
	include("mail-template.php");
	$message = ob_get_contents();
	ob_get_clean();

	$send = mail($to, $subject, $message, $headers);

	echo ($send ? "Mail is send" : "There was an error" );



