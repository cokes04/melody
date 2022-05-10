package com.example.melody;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class GenerateActivity extends AppCompatActivity {

    private ImageView uploaded_image_view;
    private Button cammera_button;
    private Button gallery_button;

    private Uri photoUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_generate);

        uploaded_image_view = findViewById(R.id.uploaded_image_view);

        cammera_button = findViewById(R.id.take_pictures_button);
        cammera_button.setOnClickListener( (View v) -> {
            Intent i = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

            try {
                File photoFile = createImageFile();
                photoUri = FileProvider.getUriForFile(this, getPackageName() + ".fileprovider", photoFile);
                i.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);
                startActivityForResult(i, 0);

            } catch (IOException ex) {

            }

        });

        gallery_button = findViewById(R.id.image_upload_button);
        gallery_button.setOnClickListener( (View v) -> {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT) ;
            intent.setType("image/*");
            intent.setAction(Intent.ACTION_GET_CONTENT);
            startActivityForResult(intent, 1);
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == 0 && resultCode == RESULT_OK) {
            uploaded_image_view.setImageURI(photoUri);
        }

        if(requestCode == 1 && resultCode == RESULT_OK) {
            Uri uri = data.getData();
            uploaded_image_view.setImageURI(uri);
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