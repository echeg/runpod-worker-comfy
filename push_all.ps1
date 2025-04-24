$tag = "0.4.3"
$repo = "echeg"
$parts = @("dev", "fill", "depth", "canny")

foreach ($part in $parts) {
    $image = "$repo/flux1-$part-nodes:$tag"
    Write-Host "Pushing $image ..."
    docker push $image
}

Write-Host "All done."