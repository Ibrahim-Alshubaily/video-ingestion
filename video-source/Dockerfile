FROM alpine:latest

RUN apk add --no-cache ffmpeg

# CMD ffmpeg -stream_loop -1 -re -i /sample.mp4 -an -c:v copy -f rtsp rtsp://video-relay:8554/mystream
CMD ffmpeg -stream_loop -1 -re -i /sample.mp4 \
    -an -c:v libx264 -vf scale=1280:720,fps=15 -b:v 1M -preset ultrafast \
     -rtsp_transport tcp -f rtsp rtsp://video-relay:8554/mystream