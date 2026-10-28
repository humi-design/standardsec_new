<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $customerName = $_POST["customer_name"];
    $customerEmail = $_POST["customer_email"];
    $complaint = $_POST["complaint"];
    $email1=$_POST['email1']
    
    // Generate a random ticket number
    $ticketNumber = mt_rand(1000, 9999);
    
    // Send email to your team
    $toUs = $email1; // Replace with your teams email address
    $subjectUs = "Complaint Ticket #$ticketNumber";
    $messageUs = "A new complaint has been logged with ticket number #$ticketNumber.\n\nCustomer Name: $customerName\nCustomer Email: $customerEmail\nComplaint: $complaint";
    mail($toUs, $subjectUs, $messageUs);
    
    // Send email to the customer
    $toCustomer = $customerEmail;
    $subjectCustomer = "Complaint Ticket Logged";
    $messageCustomer = "Hello $customerName,\n\nYour complaint has been logged. Your ticket number is #$ticketNumber. We will get back to you soon.\n\nThank you!";
    mail($toCustomer, $subjectCustomer, $messageCustomer);
}
?>