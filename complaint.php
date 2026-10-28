<?php
//session_start(); // Start the session

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $client_code=$_POST['client_code']
    $customerName = $_POST["customer_name"];
    $customerEmail = $_POST["customer_email"];
    $complaint = $_POST["complaint"];
    
    // Generate a random ticket number
    $ticketNumber = mt_rand(1000, 9999);
    
    // Send email to your team
    $toUs = "grievance@standardsec.com"; // Replace with your teams email address
    $subjectUs = "Complaint Ticket #$ticketNumber";
    $messageUs = "A new complaint has been logged with ticket number #$ticketNumber.\n\nCustomer Name: $customerName\nClient code or Pan card no: $client_code\nCustomer Email: $customerEmail\nComplaint: $complaint";
    $headersUs = "From: grievance@standardsec.com";
    mail($toUs, $subjectUs, $messageUs,$headersUs);
    
    // Send email to the customer
    $toCustomer = $customerEmail;
    $subjectCustomer = "Complaint Ticket Logged";
    $messageCustomer = "Hello $customerName,\n\nYour complaint has been logged. Your ticket number is #$ticketNumber. We will get back to you soon.\n\nThank you!";
    $headersCustomer = "From: grievance@standardsec.com";
    mail($toCustomer, $subjectCustomer, $messageCustomer,$headersCustomer);
    
      // Set success flag in session
    //$_SESSION["form_submitted"] = true;
    
    
    // Redirect to complaint.html
    //header("Location: complaint_new.html");
    //exit;
    
     if (mailmail($toUs, $subjectUs, $messageUs,$headersUs) and mail($toCustomer, $subjectCustomer, $messageCustomer,$headersCustomer)) {
        header("Location: complaint_new.html?status=success");
        exit();
    } else {
        echo "Error sending email.";
    }
}
?>