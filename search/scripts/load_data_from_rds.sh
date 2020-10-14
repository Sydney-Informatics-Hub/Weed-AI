#!/usr/bin/env zsh
# Clean refresh of ES data and thumbnails given path to RDS
# For use by the project team at the University of Sydney

# TODO: make elastic index name configurable and/or use index aliases to make the change atomic
# TODO: handle demo mode, e.g. to export random 10 images from each dataset

set -ex

mypath=$0:A
repo_root=$(dirname "$mypath")/../../

tmpd=$(mktemp -d)
trap 'rm -rf "$tmpd"' EXIT

usage() {
	echo $0 "[-r /path/to/rds] [-H http://elastic:9200] [OPTIONS]" >&2
	echo Options: >&2
	echo " -r|--rds      Specify the path to the iweeds RDS" >&2
	echo " -H|--host     Specify the elastic host and port" >&2
	echo " --no-purge    Do not purge the existing index on elastic" >&2
	echo " --no-thumbs   Do not copy thumbnails into the static file server" >&2
	echo " --wipe-thumbs Remove any existing thumbnails on static file server" >&2
	echo " --no-venv     Use the current Python environment instead of a fresh install" >&2
	echo " --demo        Only index a small sample for demonstration" >&2
	exit 1
}

if [ -d /Volumes/research-data/PRJ-iweeds ]
then
	rds_root=/Volumes/research-data/PRJ-iweeds 
else
	rds_root=/rds/PRJ-iweeds
fi
elastic_host=http://localhost:9200
get_thumbs=1
wipe_thumbs=0
demo_mode=0
purge_index=1
install_venv=1

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) usage ;;
        -r|--rds) rds_root="$2"; shift ;;
        -H|--host) elastic_host="$2"; shift ;;
		--no-purge) purge_index=0; shift ;;
		--no-thumbs) get_thumbs=0; shift ;;
		--wipe-thumbs) wipe_thumbs=1; shift ;;
		--no-venv) install_venv=0; shift ;;
		--demo) demo_mode=1; shift ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done

if [ "$get_thumbs" = 1 ]
then
	if [ "$wipe_thumbs" = 1 ]
	then
		rm -rf "$repo_root"/search/public/thumbnails
	fi
	mkdir -p "$repo_root"/search/public/thumbnails
	"$repo_root"/search/scripts/download_test_thumbnails.sh --rds "$rds_root"
fi

if [ "$purge_index" = 1 ]
then
	curl -X DELETE $elastic_host"/weedid?pretty"
fi

if [ "$install_venv" = 1 ]
then
	# setup Python environment with weedcoco installed
	virtualenv $tmpd/venv --python "$(which python3)"
	set +e
	source $tmpd/venv/bin/activate
	set -e
	test -n "$VIRTUAL_ENV"
	pip install -e "$repo_root"
fi

index_bulk() {
    python "$repo_root"'/search/scripts/weedcoco-to-elastic-index-bulk.py' "$@" |
		curl -X POST $elastic_host/_bulk -H 'Content-Type: application/json' --data-binary @-
}

python -m weedcoco.importers.deepweeds \
	--labels-dir "$rds_root"/external_datasets/raw/deepweeds/DeepWeeds/labels \
	--image-dir "$rds_root"/external_datasets/raw/deepweeds/DeepWeeds/images \
	-o $tmpd/deepweeds.weedcoco
cat $tmpd/deepweeds.weedcoco | index_bulk --thumbnail-dir deepweeds

python -m weedcoco.importers.cwfid \
	--annotations-dir "$rds_root"/external_datasets/raw/cwfid/dataset/annotations \
	--image-dir "$rds_root"/external_datasets/raw/cwfid/dataset/images \
	--split-path "$rds_root"/external_datasets/raw/cwfid/dataset/train_test_split.yaml \
	-o $tmpd/cwfid.weedcoco
cat $tmpd/cwfid.weedcoco | index_bulk --thumbnail-dir deepweeds

dir=$rds_root/data/raw/SOLES/narrabri/2019-winter/20190728
python -m weedcoco.importers.voc \
	--voc-dir $dir/voc \
	--image-dir $dir/img \
	--category-name-map $dir/category-name-map.yaml \
	--collection $dir/collection.yaml \
	--agcontext $dir/agcontext.yaml \
	-o $tmpd/coco_from_voc-test.weedcoco
cat $tmpd/coco_from_voc-test.weedcoco | index_bulk --thumbnail-dir artificial
