package com.melody.ui;

import android.content.Intent;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.melody.ui.api.GenerateMusicRequest;
import com.melody.ui.api.GenerateMusicResponse;
import com.melody.ui.api.MusicApi;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class GenerateMusicActivity extends AppCompatActivity {
    private MusicApi musicApi;
    private Retrofit retrofit;
    private OkHttpClient okHttpClient;

    private ImageView uploadedImageView;
    private Button cammeraButton;
    private Button galleryButton;
    private Button generateButton;
    private Uri photoUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_generate_music);

        okHttpClient = new OkHttpClient.Builder()
                .connectTimeout(5, TimeUnit.MINUTES)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();

        retrofit = new Retrofit.Builder()
                .baseUrl(musicApi.GENERATE_BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .client(okHttpClient)
                .build();
        musicApi = retrofit.create(MusicApi.class);

        uploadedImageView = findViewById(R.id.uploaded_image_view);

        cammeraButton = findViewById(R.id.take_pictures_button);
        cammeraButton.setOnClickListener( (View v) -> {
            Intent i = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

            try {
                File photoFile = createImageFile();
                photoUri = FileProvider.getUriForFile(this, getPackageName() + ".fileprovider", photoFile);
                i.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);
                startActivityForResult(i, 0);

            } catch (IOException ex) {}

        });

        galleryButton = findViewById(R.id.upload_image_button);
        galleryButton.setOnClickListener( (View v) -> {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT) ;
            intent.setType("image/*");
            intent.setAction(Intent.ACTION_GET_CONTENT);
            startActivityForResult(intent, 1);
        });

        generateButton = findViewById(R.id.generate_music_button);
        generateButton.setOnClickListener( (View v) -> {
            // 여기서 작곡 모델 돌려서
            // 음악 받고 저장 후


            Emotion emotion = Emotion.delighted;
            int music_len = 100;
            int noise_num = 50;
            getMusic(emotion, music_len, noise_num);
            //if(작곡 성공시)
            /*if (true) {
                Intent intent = new Intent(getApplicationContext(), PlayMusicActivity.class);
                intent.putExtra(PlayMusicActivity.SET_MUSIC_KEY, R.raw.test*//*작곡된 음악 파일 ID*//*);
                startActivity(intent);
            }
            //else(작곡 실패시)
            else {
                Toast.makeText(GenerateMusicActivity.this, "작곡 실패!", Toast.LENGTH_SHORT).show();
            }*/
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == 0 && resultCode == RESULT_OK) {
            uploadedImageView.setImageURI(photoUri);
        }

        if(requestCode == 1 && resultCode == RESULT_OK) {
            Uri uri = data.getData();
            uploadedImageView.setImageURI(uri);
        }


    }
    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_MELODY_" + timeStamp;
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        File image = File.createTempFile( imageFileName, ".jpg", storageDir);
        return image;
    }

    private void getMusic(Emotion emotion, int noise_num, int music_len) {
        GenerateMusicRequest  request = new GenerateMusicRequest(
                emotion.name(),
                noise_num,
                music_len
        );

        System.out.println(request.toString());
        Call<GenerateMusicResponse> call = musicApi.generateMusic(request);
        Toast.makeText(GenerateMusicActivity.this, "작곡 중입니다.", Toast.LENGTH_SHORT).show();

        call.enqueue(new Callback<GenerateMusicResponse>() {
            @Override
            public void onResponse(Call<GenerateMusicResponse> call, Response<GenerateMusicResponse> response) {
                if (response.isSuccessful()) {
                    GenerateMusicResponse data = response.body();
                    System.out.println(data.toString());

                } else {
                    Toast.makeText(GenerateMusicActivity.this, "음악 생성에 실패하였습니다.", Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<GenerateMusicResponse> call, Throwable t) {
                Toast.makeText(GenerateMusicActivity.this, "음악 생성에 실패하였습니다.", Toast.LENGTH_SHORT).show();
                t.printStackTrace();
            }
        });
    }
}