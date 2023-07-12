<?php
//set working files
$file = "servers.txt";
$filetrans = "trans.txt";

//set variables
$linebreak = "\r\n";
$break = ",";
$ip=$_SERVER['REMOTE_ADDR'];
$time = date("H");

//lobby takes input from url as *.php?lobby=blah
$lobby = $_GET['lobby'];

//print input for user
echo "<font face='Verdana' size='3'><b>Svr Name= $lobby</b>"; 
echo "<font face='Verdana' size='3'><b> IP Address= $ip</b>"; 
echo "<font face='Verdana' size='3'><b> Time= $time</b>";

//writes user input to end of $file
$fr = fopen($file,"a");
fwrite($fr,$lobby);
fwrite($fr,$break);
fwrite($fr,$ip);
fwrite($fr,$break);
fwrite($fr,$time);
fwrite($fr,$linebreak);
fclose($fr);

//deletes contents of $filetrans
$handle = fopen($filetrans, "w");
fclose($handle);

//reads in contents of $file and sorts each line into sections
$fo = fopen($file,"r");
while ($line = fgetcsv($fo, 2000, ",")) {
      $svrname = $line[0];
      $ipaddy = $line[1];
      $oldtime = $line[2];

//checks time of server entries in $file against current time and takes abs value
$sub=$time - $oldtime;
$newsub=abs($sub);
 if ($newsub > 1) {
 echo "<font face='Verdana' size='3'><b><br>ignoring dead server</b>";
}
else {
//if server entry passed time check, write to $filetrans
$fwte = fopen($filetrans,"a");
fwrite($fwte,$svrname);
fwrite($fwte,$break);
fwrite($fwte,$ipaddy);
fwrite($fwte,$break);
fwrite($fwte,$oldtime);
fwrite($fwte,$linebreak);
fclose($fwte);
}



}

fclose($fo);

//copy $filetrans over $file
copy($filetrans, $file);

?>