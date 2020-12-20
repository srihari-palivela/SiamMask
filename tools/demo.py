# --------------------------------------------------------
# SiamMask
# Licensed under The MIT License
# Written by Qiang Wang (wangqiang2015 at ia.ac.cn)
# --------------------------------------------------------
import glob
import json

from tools.test import *

parser = argparse.ArgumentParser(description='PyTorch Tracking Demo')

parser.add_argument('--resume', default='', type=str, required=True,
                    metavar='PATH',help='path to latest checkpoint (default: none)')

parser.add_argument('--config', dest='config', default='config_davis.json',
                    help='hyper-parameter of SiamMask in json format')
parser.add_argument('--base_path', default='../../data/tennis', help='datasets')
parser.add_argument('--cpu', action='store_true', help='cpu mode')
parser.add_argument('--resume-prediction', default=None, type=str,
                    metavar='PATH',help='path to latest checkpoint (default: none)')

parser.add_argument('--output-file', default="predictions.json", type=str,
                    metavar='PATH',help='path to latest checkpoint (default: none)')

args = parser.parse_args()

def read_ims(img_files):
    for imf in img_files:
        yield (imf, cv2.imread(imf))

if __name__ == '__main__':

    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True

    # Setup Model
    cfg = load_config(args)
    print(cfg,'\n', args)
    from custom import Custom
    siammask = Custom(anchors=cfg['anchors'])
    if args.resume:
        assert isfile(args.resume), 'Please download {} first.'.format(args.resume)
        siammask = load_pretrain(siammask, args.resume)

    siammask.eval().to(device)
    # Parse Image file
    img_files = sorted(glob.glob(join(args.base_path, '*.jp*')))

    # Check if resume prediction
    if args.resume_prediction:
        print("Here")
        idx = img_files.index(args.resume_prediction)
        print("Index of that shit", idx)
        img_files = img_files[idx:]
    predictions = {}
    try:
        predictions = json.load(open(args.output_file,"r"))
    except:
        pass

    # Select ROI
    ims = cv2.imread(img_files[0])
    cv2.namedWindow("SiamMask", cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty("SiamMask", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    try:
        init_rect = cv2.selectROI('SiamMask', ims, False, False)
        x, y, w, h = init_rect
    except:
        exit()



    ims = read_ims(img_files)
    toc = 0
    for f, (im_name, im) in enumerate(ims):
        print("Current : ", im_name)
        tic = cv2.getTickCount()
        if f == 0:  # init
            target_pos = np.array([x + w / 2, y + h / 2])
            target_sz = np.array([w, h])
            state = siamese_init(im, target_pos, target_sz, siammask, cfg['hp'], device=device)  # init tracker
        elif f > 0:  # tracking
            state = siamese_track(state, im, mask_enable=True, refine_enable=True, device=device)  # track
            predictions[im_name] = list(state['target_pos'])
            location = state['ploygon'].flatten()
            mask = state['mask'] > state['p'].seg_thr

            im[:, :, 2] = (mask > 0) * 255 + (mask == 0) * im[:, :, 2]
            cv2.polylines(im, [np.int0(location).reshape((-1, 1, 2))], True, (0, 255, 0), 3)
            cv2.imshow('SiamMask', im)
            key = cv2.waitKey(1)
            if key > 0:
                break
        toc += cv2.getTickCount() - tic
    toc /= cv2.getTickFrequency()
    fps = f / toc
    print("Stopped at : ", im_name)
    json.dump(predictions, open(args.output_file,"w"))
    print('SiamMask Time: {:02.1f}s Speed: {:3.1f}fps (with visulization!)'.format(toc, fps))
