<html>
<head>
<title></title>
 
</head>
<form action="" method="GET">
 
 <input type="submit" name="ekyc" value="ekyc" onclick="ekyc()" />
  
</form>
</html>
<?php

ekyc();

@$key 	= "AUTHTOKEN";
@$refId1 = rand(10,100);            
@$etoken1 = $_GET['eToken'];  

$PanName = "NA";
$PanNo = "NA";
$PanExem = "N";
$KycEmpCode = "NA";
$KycEmpName = "NA";
$MobileNo = "NA";
$EmailId = "NA";
$DOB = "NA";
$KycEmpBranch = "NA";
$KycEmpDesig = "NA";

if(isset($key))
{
	 $OLAOKey = "671EFD274DC49FB";
	 $RefId  = $refId1;
 
 	if(strtoupper($key) == 'AUTHTOKEN'){
		header("Location: https://testolao.cvlindia.com/NewCustomer/".$OLAOKey."/".$RefId."/".$etoken1."/".$PanName."/".$PanNo."/".$PanExem."/".$KycEmpCode."/".$KycEmpName."/".$MobileNo."/".$EmailId."/".$DOB."/".$KycEmpBranch."/".$KycEmpDesig); 
		die();
	}
}

 
function ekyc(){
	$OLAOKey = "OLAO_KEY";
	$RefId  = "UNIQUE_ID";

$etoken = "0"; // FOR FIRST HIT OF TRANSACTION E-TOKEN SHOULD BE 0 



$PanName = "NA";
$PanNo = "NA";
$PanExem = "N";
$KycEmpCode = "NA";
$KycEmpName = "NA";
$MobileNo = "NA";
$EmailId = "NA";
$DOB = "NA";
$KycEmpBranch = "NA";
$KycEmpDesig = "NA";

//  header("Location:https://testolao.cvlindia.com/NewCustomer/".$OLAOKey."/".$RefId."/".$etoken."/".$PanName."/".$PanNo."/".$PanExem."/".$KycEmpCode."/".$KycEmpName."/".$MobileNo."/".$EmailId."/".$DOB."/".$KycEmpBranch."/".$KycEmpDesig);  
 
  $url="https://testolao.cvlindia.com/NewCustomer/".$OLAOKey."/".$RefId."/".$etoken."/".$PanName."/".$PanNo."/".$PanExem."/".$KycEmpCode."/".$KycEmpName."/".$MobileNo."/".$EmailId."/".$DOB."/".$KycEmpBranch."/".$KycEmpDesig;

  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, $url);
  curl_setopt($ch, CURLOPT_HEADER, true);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // Must be set to true so that PHP follows any "Location:" header
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  
  $a = curl_exec($ch); // $a will contain all headers
  
  $url = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL); // This is what you need, it will return you the last effective URL
  $url_Array = parse_url($url);
  $a = explode("=",$url_Array["query"]);

  $_GET['eToken'] = $a[3];

}


?>