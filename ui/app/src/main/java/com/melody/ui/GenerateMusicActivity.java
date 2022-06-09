package com.melody.ui;

import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.Cursor;
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
import java.time.LocalDateTime;
import java.util.Date;
import java.util.Random;
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

    private DownloadManager downloadManager;
    private Long downloadQueueId;
    private File downloadedfile;
    private File directory = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS + "/melody/musics");

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
            int music_len = 170;
            int noise_num = 3;
            getMusic(emotion, noise_num, music_len);
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

    @Override
    public void onResume(){
        super.onResume();
        IntentFilter completeFilter = new IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE);
        registerReceiver(downloadCompleteReceiver, completeFilter);
    }

    @Override
    public void onPause(){
        super.onPause();
        unregisterReceiver(downloadCompleteReceiver);
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
        System.out.println("Generate Music Requset");
        System.out.println(request.toString());
        Call<GenerateMusicResponse> call = musicApi.generateMusic(request);
        Toast.makeText(GenerateMusicActivity.this, "작곡 중입니다.", Toast.LENGTH_SHORT).show();

        call.enqueue(new Callback<GenerateMusicResponse>() {
            @Override
            public void onResponse(Call<GenerateMusicResponse> call, Response<GenerateMusicResponse> response) {
                if (response.isSuccessful()) {
                    GenerateMusicResponse data = response.body();
                    System.out.println("Generate Music Response");
                    System.out.println(data.toString());

                    Uri uri = Uri.parse(data.getUrl());
                    downloadMusic(uri);

                } else {
                    System.out.println("Generate Music Failed");
                    System.out.println(response.toString());
                    Toast.makeText(GenerateMusicActivity.this, "음악 생성에 실패하였습니다.", Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<GenerateMusicResponse> call, Throwable t) {
                System.out.println("Generate Music Failed");
                Toast.makeText(GenerateMusicActivity.this, "음악 생성에 실패하였습니다.", Toast.LENGTH_SHORT).show();
                t.printStackTrace();
            }
        });
    }

    private void downloadMusic(Uri url) {
        if (downloadManager == null) {
            downloadManager = (DownloadManager) GenerateMusicActivity.this.getSystemService(Context.DOWNLOAD_SERVICE);
        }

        String fileName = url.getLastPathSegment();

        if (!fileName.matches("^[0-9]+\\.mid")){
            fileName = String.valueOf((int) Math.random() * (99999 - 10000 + 1) + 10000);
            fileName += ".mid";
        }
        File file = new File(directory + "/" + fileName);

        System.out.println("Download Music Start: " + url.toString());
        System.out.println("File Path: " + file.toString());
        DownloadManager.Request request = new DownloadManager.Request(url)
                .setTitle("Downloading!")
                .setDescription("Downloading!!")
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationUri(Uri.fromFile(file))
                .setAllowedOverMetered(true)
                .setAllowedOverRoaming(true);

        downloadQueueId = downloadManager.enqueue(request);
        downloadedfile = file;
    }


    private BroadcastReceiver downloadCompleteReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {

            long reference = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1);

            if(downloadQueueId == reference){
                DownloadManager.Query query = new DownloadManager.Query();  // 다운로드 항목 조회에 필요한 정보 포함
                query.setFilterById(reference);
                Cursor cursor = downloadManager.query(query);

                cursor.moveToFirst();

                int columnIndex = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS);
                int columnReason = cursor.getColumnIndex(DownloadManager.COLUMN_REASON);

                int status = cursor.getInt(columnIndex);
                int reason = cursor.getInt(columnReason);

                cursor.close();

                switch (status) {
                    case DownloadManager.STATUS_SUCCESSFUL :
                        Toast.makeText(GenerateMusicActivity.this, "다운로드를 완료하였습니다.", Toast.LENGTH_SHORT).show();
                        System.out.println("Success Download Music");
                        if (downloadedfile != null) {
                            Intent intent1 = new Intent(getApplicationContext(), PlayMusicActivity.class);
                            intent1.putExtra(PlayMusicActivity.SET_MUSIC_KEY, downloadedfile.getPath());
                            startActivity(intent1);
                        }
                        break;

                    case DownloadManager.STATUS_PAUSED :
                        downloadedfile = null;
                        Intent intent2 = new Intent(getApplicationContext(), MainActivity.class);
                        startActivity(intent2);
                        Toast.makeText(GenerateMusicActivity.this, "다운로드가 중단되었습니다.", Toast.LENGTH_SHORT).show();
                        break;

                    case DownloadManager.STATUS_FAILED :
                        downloadedfile = null;
                        Intent intent3 = new Intent(getApplicationContext(), MainActivity.class);
                        startActivity(intent3);
                        Toast.makeText(GenerateMusicActivity.this, "다운로드가 취소되었습니다.", Toast.LENGTH_SHORT).show();
                        break;
                }
            }
        }
    };
}