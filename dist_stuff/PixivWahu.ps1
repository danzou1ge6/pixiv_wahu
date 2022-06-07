$argsArray = ""
foreach ($arg in $args) {
    $argsArray += "'$($arg)', "
}

$argsArray = "[" + $argsArray + "]"

.\python -c "from wahu_backend import run; run($($argsArray), standalone=False);"
