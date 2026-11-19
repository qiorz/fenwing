import io
p='/mnt/d/ff-ohos/scripts/soak-test.ps1'
s=io.open(p,encoding='utf-8').read()
old="""  $rssNav = Get-Rss $appPid3

  $rows += [pscustomobject]@{"""
assert s.count(old)==1
new="""  $rssNav = Get-Rss $appPid3

  # close the second tab and sample memory after reclamation
  & $hdc -t $target shell "uitest uiInput click 1185 1673" 2>&1 | Out-Null
  Start-Sleep -Seconds 2
  $rssClose = Get-Rss (Get-AppPid)
  $thresholdKb = 450000
  $overThreshold = ($rssNav -gt $thresholdKb)
  if ($overThreshold) {
    Add-Content -Path $crashes -Value "=== cycle$i rss over threshold: $rssNav KB ===" -Encoding UTF8
  }

  $rows += [pscustomobject]@{"""
s=s.replace(old,new)
s=s.replace("""    rss_nav_kb = $rssNav
    mem_available_kb = $memAvail
    crashed = $crashed
  }
  Write-Output ("cycle {0}: launch={1}KB tabs={2}KB switch={3}KB nav={4}KB crashed={5}" -f $i, $rssLaunch, $rssTabs, $rssSwitch, $rssNav, $crashed)""",
"""    rss_nav_kb = $rssNav
    rss_close_kb = $rssClose
    mem_available_kb = $memAvail
    crashed = $crashed
    over_threshold = $overThreshold
  }
  Write-Output ("cycle {0}: launch={1}KB tabs={2}KB switch={3}KB nav={4}KB close={5}KB crashed={6} over={7}" -f $i, $rssLaunch, $rssTabs, $rssSwitch, $rssNav, $rssClose, $crashed, $overThreshold)""")
io.open(p,'w',encoding='utf-8').write(s)
print('soak v2 patched')
