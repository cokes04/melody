package com.example.melody;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.media.MediaPlayer;
import android.os.Handler;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ProgressBar;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

public class PlayMusicActivity extends AppCompatActivity {
    public static final int NON_EXISTENT_MUSIC = -1;
    public static final String SET_MUSIC_KEY = "music";

    private MediaPlayer mediaPlayer;

    private Handler seekbarUpdateHandler = new Handler();
    private Runnable updateSeekbar = getUpdateSeekbarRunnable();

    private SeekBar seekbar;

    private Button playStopButton;
    private Button uploadMusicButton;

    private int musicToPlay = NON_EXISTENT_MUSIC;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_play_music);

        setMusicToPlayFromActivity();

        //테스트용
        if (!isExistsMusic())
            musicToPlay = R.raw.test;

        seekbar = (SeekBar) findViewById(R.id.seekBar);
        playStopButton = (Button) findViewById(R.id.control_music_button);
        uploadMusicButton = (Button) findViewById(R.id.upload_music_button);

        playStopButton.setOnClickListener( (View view) -> {
            if (!isExistsMusic()){
                Toast.makeText(PlayMusicActivity.this, "음악을 가져와주세요.", Toast.LENGTH_SHORT).show();
                return;
            }

            if (mediaPlayer == null) {
                setMediaPlayer();
                seekbar.setOnSeekBarChangeListener( getOnSeekBarChangeListener() );
            }

            if(mediaPlayer.isPlaying()){
                mediaPlayer.pause();
                playStopButton.setText("재생");
                seekbarUpdateHandler.removeCallbacks(updateSeekbar);
            }else {
                mediaPlayer.start();
                playStopButton.setText("정지");
                seekbarUpdateHandler.postDelayed(updateSeekbar, 0);
            }


        });

        uploadMusicButton.setOnClickListener((View view) ->{
            // 음악 불러오는 기능 구현
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        seekbarUpdateHandler.removeCallbacks(updateSeekbar);
        seekbar = null;
        clearMediaPlayer();
    }

    private void setMusicToPlayFromActivity(){
        Intent intent = getIntent();
        int music = intent.getIntExtra(SET_MUSIC_KEY, -1);
        musicToPlay = music;
    }

    private void setMediaPlayer() {
        mediaPlayer = MediaPlayer.create(PlayMusicActivity.this, musicToPlay);
        seekbar.setMax( mediaPlayer.getDuration() );

        mediaPlayer.setOnCompletionListener( (MediaPlayer mediaPlayer) -> {
            seekbarUpdateHandler.removeCallbacks(updateSeekbar);
            mediaPlayer.release();
            this.mediaPlayer = null;
            playStopButton.setText("재생");
        });
    }

    private Runnable getUpdateSeekbarRunnable() {
       return new Runnable() {
            @Override
            public void run() {
                seekbar.setProgress(mediaPlayer.getCurrentPosition());
                seekbarUpdateHandler.postDelayed(this, 50);
            }
        };
    }

    private SeekBar.OnSeekBarChangeListener getOnSeekBarChangeListener() {
        return new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if(fromUser)
                    mediaPlayer.seekTo(progress);
            }
        };
    }

    private void clearMediaPlayer() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.release();
        }
        mediaPlayer = null;
    }
    private boolean isExistsMusic(){
        return musicToPlay != NON_EXISTENT_MUSIC;
    }
}