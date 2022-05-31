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

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class GenerateMusicActivity extends AppCompatActivity {
    private ImageView uploadedImageView;
    private Button cammeraButton;
    private Button galleryButton;
    private Button generateButton;
    private Uri photoUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_generate_music);

        uploadedImageView = findViewById(R.id.uploaded_image_view);

        cammeraButton = findViewById(R.id.take_pictures_button);
        cammeraButton.setOnClickListener( (View v) -> {
            Intent i = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

            try {
                File photoFile = createImageFile();
                photoUri = FileProvider.getUriForFile(this, getPackageName() + ".fileprovider", photoFile);
                i.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);
                startActivityForResult(i, 0);

            } catch (IOException ex) {

            }

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

            //if(작곡 성공시)
            if (true) {
                Intent intent = new Intent(getApplicationContext(), PlayMusicActivity.class);
                intent.putExtra(PlayMusicActivity.SET_MUSIC_KEY, R.raw.test/*작곡된 음악 파일 ID*/);
                startActivity(intent);
            }
            //else(작곡 실패시)
            else {
                Toast.makeText(GenerateMusicActivity.this, "작곡 실패!", Toast.LENGTH_SHORT).show();
            }
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
}