package capture

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"video-source/internal/config"

	"gocv.io/x/gocv"
)

func Start() error {
	cam, err := openVideoCapture()
	if err != nil {
		return err
	}
	defer cam.Close()

	frame := gocv.NewMat()
	defer frame.Close()

	fmt.Println("Started capturing frames...")
	return captureFrames(cam, &frame)
}

func openVideoCapture() (*gocv.VideoCapture, error) {
	var cam *gocv.VideoCapture
	var err error

	for attempt := 1; attempt <= config.MaxRetries; attempt++ {
		cam, err = gocv.OpenVideoCapture(config.RTSPURL)
		if err == nil && cam.IsOpened() {
			fmt.Printf("Connected to stream on attempt %d\n", attempt)
			return cam, nil
		}

		fmt.Printf("Attempt %d failed: %v\n", attempt, err)
		if cam != nil {
			cam.Close()
		}

		if attempt < config.MaxRetries {
			time.Sleep(time.Duration(config.RetryInterval) * time.Second)
		}
	}

	return nil, fmt.Errorf("failed to connect after %d attempts", config.MaxRetries)
}

func captureFrames(cam *gocv.VideoCapture, frame *gocv.Mat) error {
	const batchSize = 100
	var batchStart = time.Now()

	for count := 1; ; count++ {
		if !cam.Read(frame) || frame.Empty() {
			return fmt.Errorf("failed to read frame")
		}

		if err := saveFrame(frame, count); err != nil {
			fmt.Printf("Error saving frame %d: %v\n", count, err)
			continue
		}

		if count%batchSize == 0 {
			duration := time.Since(batchStart)
			fps := float64(batchSize) / duration.Seconds()
			fmt.Printf("Batch %d-%d: %.2f seconds (%.2f fps)\n",
				count-batchSize+1, count, duration.Seconds(), fps)
			batchStart = time.Now()
		}
	}
}

func saveFrame(frame *gocv.Mat, count int) error {
	dir := filepath.Join(config.OutputDir, time.Now().Format("2006_01_02"))
	if err := os.MkdirAll(dir, os.ModePerm); err != nil {
		return fmt.Errorf("failed to create directory: %v", err)
	}

	path := filepath.Join(dir, fmt.Sprintf("frame_%d.jpg", count))
	if !gocv.IMWrite(path, *frame) {
		return fmt.Errorf("failed to save frame")
	}

	return nil
}
