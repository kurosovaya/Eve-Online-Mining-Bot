param(
    [Parameter(Mandatory=$true)][string]$DatasetRoot,
    [Parameter(Mandatory=$true)][string]$OutJson,
    [Parameter(Mandatory=$true)][string]$ImageRootUrl
)

label-studio-converter import yolo `
-i "$DatasetRoot"`
-o  "$OutJson"`
 --image-root-url "$ImageRootUrl"