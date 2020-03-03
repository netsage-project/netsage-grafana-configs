#Probably a better way of doing this
$res = (docker ps -a | Select-String -Pattern dashboard | ForEach-Object {
 $data = $_ -split " "
 "{0}{1}{2}" -f $data[2],$data[3],$data[0],$data[5],$data[1],
     $data[4],$data[6],$data[7]
}
 )

docker exec -it $res bash
