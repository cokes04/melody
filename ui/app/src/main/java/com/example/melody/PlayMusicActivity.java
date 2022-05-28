package com.example.melody;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.media.MediaPlayer;
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
        seekbar.setOnSeekBarChangeListener( getOnSeekBarChangeListener() );

        playStopButton = (Button) findViewById(R.id.control_music_button);
        uploadMusicButton = (Button) findViewById(R.id.upload_music_button);

        playStopButton.setOnClickListener( (View view) -> {
            if (!isExistsMusic()){
                Toast.makeText(PlayMusicActivity.this, "음악을 가져와주세요.", Toast.LENGTH_SHORT).show();
                return;
            }

            if (mediaPlayer == null)
                setMediaPlayer();

            if(mediaPlayer.isPlaying()){
                mediaPlayer.pause();
                playStopButton.setText("재생");
                runSeekbar();

            }else {
                mediaPlayer.start();
                playStopButton.setText("정지");
            }
        });

        uploadMusicButton.setOnClickListener((View view) ->{
            // 음악 가져오는 기능 구현
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if(mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
        }
    }

    private void setMusicToPlayFromActivity(){
        Intent intent = getIntent();
        int music = intent.getIntExtra(SET_MUSIC_KEY, -1);
        musicToPlay = music;
    }

    private void setMediaPlayer() {
        mediaPlayer = MediaPlayer.create(PlayMusicActivity.this, musicToPlay);

        mediaPlayer.setOnCompletionListener( (MediaPlayer mediaPlayer) -> {
            mediaPlayer.release();
            playStopButton.setText("재생");
        });
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

    private void runSeekbar(){
        seekbar.setMax( mediaPlayer.getDuration() );

        // 0.5초마다 seekbar 움직임
        new Thread( () -> {
            while(mediaPlayer.isPlaying()){
                try{
                    Thread.sleep(500);
                } catch(Exception e){
                    e.printStackTrace();
                }
                seekbar.setProgress(mediaPlayer.getCurrentPosition());
            }
        }).start();
    }


    private boolean isExistsMusic(){
        return musicToPlay != NON_EXISTENT_MUSIC;
    }
}