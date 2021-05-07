import React from 'react';
import {
    ReactiveList,
} from '@appbaseio/reactivesearch';
import ResultCard from './ResultCard';
import { Helmet } from "react-helmet";


const OgThumbnail = ({ url }) => {
    const [imageDims, setImageDims] = React.useState(null);
    React.useEffect(() => {
        const img = new Image();
        img.src = url;
        img.onload = (ev) => { setImageDims({"width": ev.target.width, "height": ev.target.height}); }
    });
    return (
        <Helmet>
            <meta property="og:image" content={url} />
            {imageDims && <meta property="og:image:width" content={imageDims.width} />}
            {imageDims && <meta property="og:image:height" content={imageDims.height} />}
        </Helmet>
    );
}

const ResultsList = ({ listProps, cardProps, setOGImage, baseURL }) => {
  const computedBaseURL = baseURL || new URL(window.location.origin);
  return (
    <ReactiveList
        componentId="result"
        dataField="results"
        title="Results"
        sortOptions={[{"label": "random order", "dataField": "sortKey", "sortBy": "asc"}]}
        from={0}
        size={20}
        infiniteScroll={true}
        renderResultStats={
            function(stats){
                return (
                    <p style={{position: 'absolute', left: 0, fontSize: '0.8em'}}>{stats.numberOfResults} annotated images found</p>
                )
            }
        }
        render={({ data }) => (
          <ReactiveList.ResultCardsWrapper>
            {
              data.map((item, idx) => [<ResultCard
                key={item._id}
                item={item}
                baseURL={computedBaseURL}
                {...cardProps}
                />,
                // XXX: side-effects
                // Use the first result as the page's thumbnail for social media:
                (!setOGImage || idx !== 0) ? [] :
                  <OgThumbnail url={computedBaseURL + (item.thumbnail_bbox || item.thumbnail)} />
              ])
            }
          </ReactiveList.ResultCardsWrapper>
        )}
        {...listProps}
    />
  );
}

export default ResultsList;
