#!/bin/bash
set -e

OUT_DIR="/home/ubuntu/apps/zolu-movie/public/video"
mkdir -p "$OUT_DIR"
OUT_FILE="$OUT_DIR/goblix_intro.mp4"

echo "[1/2] Generating Cinematic Goblix 1080p 16:9 Intro..."

# Generate high quality 1080p 16:9 intro with synthesized cinematic Ta-Dum audio
ffmpeg -y \
  -f lavfi -i "color=c=black:s=1920x1080:d=4.2:r=30" \
  -f lavfi -i "sine=frequency=55:duration=4.2" \
  -f lavfi -i "sine=frequency=110:duration=4.2" \
  -f lavfi -i "sine=frequency=165:duration=4.2" \
  -f lavfi -i "anoisesrc=d=4.2:c=pink:r=48000" \
  -filter_complex "
    [0:v]
      drawbox=x=0:y=0:w=1920:h=1080:color=black@1:t=fill,
      drawbox=x='(w-800)/2':y='(h-4)/2':w='min(800,t*600)':h=4:color=#E50914@0.9:t=fill,
      drawtext=text='GOBLIX':fontcolor=#E50914:fontsize='if(lt(t,1.2),110+t*15,128)':
        x='(w-text_w)/2':y='(h-text_h)/2-30':
        shadowcolor=#E50914@0.8:shadowx=0:shadowy=0:
        alpha='if(lt(t,0.5),t*2,if(gt(t,3.2),1-(t-3.2),1))',
      drawtext=text='GOBLIX':fontcolor=white:fontsize='if(lt(t,1.2),110+t*15,128)':
        x='(w-text_w)/2':y='(h-text_h)/2-30':
        alpha='if(lt(t,0.8),t*1.2,if(gt(t,3.2),1-(t-3.2),1))',
      drawtext=text='NONTON FILM 1080P BLURAY SUBTITLE INDONESIA':fontcolor=#FFD700:fontsize=24:
        x='(w-text_w)/2':y='(h-text_h)/2+70':
        shadowcolor=black@0.9:shadowx=2:shadowy=2:
        alpha='if(lt(t,1.0),0,if(lt(t,1.8),(t-1.0)*1.25,if(gt(t,3.2),1-(t-3.2),1)))',
      fade=t=out:st=3.3:d=0.9
    [v];
    [1:a]volume=1.2,afade=t=in:st=0:d=0.1,afade=t=out:st=2.5:d=1.5[a1];
    [2:a]volume=0.8,afade=t=in:st=0:d=0.1,afade=t=out:st=2.5:d=1.5[a2];
    [3:a]volume=0.5,afade=t=in:st=0.2:d=0.2,afade=t=out:st=2.5:d=1.5[a3];
    [4:a]volume=0.08,bandpass=f=800:width_type=h:w=200,afade=t=in:st=0:d=0.3,afade=t=out:st=2.0:d=1.5[a4];
    [a1][a2][a3][a4]amix=inputs=4:duration=first[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 \
  -c:a aac -b:a 192k \
  -t 4.2 \
  "$OUT_FILE"

echo "[2/2] Successfully generated $OUT_FILE ($(stat -c%s "$OUT_FILE") bytes)"
