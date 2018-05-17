import os

if __name__ == '__main__':
    num_images = 0
    subfolders = os.listdir('./download') if os.path.exists('./download') else []
    for subfolder in subfolders:
        num_images += len(os.listdir(os.path.join('./download', subfolder, 'photo')))
        
    print('=== Tumblrer Stats ===')
    print('# of galleries:', len(subfolders))
    print('# of photos:', num_images)
    print('======================')