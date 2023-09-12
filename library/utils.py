# ---------------------------------------------------------------------------------

def stac_tile_search(collection, geom, start_date, end_date):
    """
    Log into STAC and search for a specified image collection.

    Parameters:
    ----------
    collection: list
        List of tiles found in STAC.

    geom: dict
        A dictionary of coordinates defining point location to search.

    start_date, end_date: str
        Dates to search between.

    Returns:
    -------
    found_items: list
        List of images found.
    num_tiles: int
        Num of images found.
    itemjson: json
        Json describing what search found.
    """
    search = catalog.search(
        collections=collection,
        intersects=geom,
        datetime=[start_date, end_date],
        max_items=1000,
    )

    #found_items = list(search.items()) # for pystac-client >= 0.4.0
    found_items = list(search.get_all_items())  # for pystac-client < 0.4.0

    # Need this to get the url path for downloading the files to local machine.
    itemjson = search.item_collection_as_dict() 

    # Filter out only the newest version of MODIS.
    if collection == 'prepped_inputs_mcd43a4':
        version_str = '.061_'
        new_list = [i for i in found_items if version_str in i.id]
        found_items = new_list

    found_items.reverse()  # make the results ascending in time

    num_tiles = len(found_items)
    print("Colllection: {}.  {} Images found.".format(collection, num_tiles))

    return (found_items, num_tiles, itemjson)

# ---------------------------------------------------------------------------------

def create_aoi_image_stack(asset, items, num_tiles, poly_gdf):
    '''
    Gets images, stacks them and sorts them by date and clips them down to a smaller
    AOI size.

    Parameters:
    -----------
    itmes: list 
        List of available images.
    num_tiles: int
        Number of tiles to download (days)
    asset: str
        Name of asset to get.
    poly_gdf: geodataframe
        A polygon to which the dataarray image will be clipped.

    Returns:
    --------
    aoi_stack_ds: dataset as FH_StackedDataset object.
        Stack of images clipped to AOI.

    '''
    images = FH_Hydrosat(items[:num_tiles], asset=asset)

    # Stacks all the files into a dataset and then return a FH_StackedDataset object.
    stacked_images = images.stack()
    # Sort the dataset by time.
    ds = stacked_images.ds.sortby('time')
    
    # Clip the big image into a smaller image using the poly_gdf AOI
    # we defined in the Analysis Setup code cell.
    clipped = FH_StackedDataset(ds.rio.clip(poly_gdf.geometry, all_touched=True, drop=True))
    aoi_stack_ds = clipped.ds

    return (aoi_stack_ds)

# ---------------------------------------------------------------------------------   
def extract_time_series(items, asset, bbox, tol, pad, band, var_name):
    '''
    Uses FH_Hydrosat class method point_time_series_from_items()
    to extract only a time-series.

    Parameters:
    -----------
    items: list
        Image items returned from STAC search.
    bbox: 
        Bounding box of coordinates for seacrh site.
    tol: int
        A search parameter in meters for finding point data.
    var_name: str
        Dataframe column name for data extracted.
    asset: str
        Search parameter for type of asset to be searched.
    
    Returns:
    -------
    lst_df: dataframe
        Dataframe containing date time series.
    '''
    # Sample the LST items.
    lst_res = FH_Hydrosat(items, asset=asset)

    # Set the point for time-series extraction.
    point_wgs84 = Point(box(*bbox).centroid.x, box(*bbox).centroid.y)
    
    # Extract time-series data using function.
    band = int(band) # band needs to be an int because it comes in as a string.
    lst_k  = lst_res.point_time_series_from_items(point_wgs84, tol=tol, nproc=6, band=band) 

    # Create a datetime dataframe
    lst_dt = lst_res.datetime
    lst_df = pd.DataFrame({var_name: lst_k,
                       'datetime': pd.to_datetime(lst_dt)}).sort_values(by='datetime')
    
    # Get the date in the correct/consistent format.
    lst_df['date'] = [t.to_pydatetime().strftime('%Y-%m-%d') for t in lst_df['datetime']]
    lst_df['date'] = pd.to_datetime(lst_df['date'])
    lst_df.drop(columns='datetime', inplace=True)
    lst_df.set_index('date', drop=True, inplace=True)
    
    return (lst_df)

# --------------------------------------------------------------------------------- 
def read_ameriflux(data_path):
    '''
    Reads, extracts & processes meteorological csv file and returns data in a dataframe.

    Parameters:
    -----------
    data_path: str
        Path to the met datafile
    
    Returns:
    -------
    df: dataframe
        Dataframe containing met time series.
    '''
   
    print('Reading file {}'.format(data_path))

    df = pd.read_csv(data_path, header=0, na_values=[-9999.000000])

    # Save value column names
    value_cols = df.columns[2:]

    # Convert timestamp objects
    df['start'] = df['TIMESTAMP_START'].apply(
        lambda x: datetime.strptime(str(x), "%Y%m%d%H%M.0")
    )
    df['end'] = df['TIMESTAMP_END'].apply(
        lambda x: datetime.strptime(str(x), "%Y%m%d%H%M.0")
    )

    # Convert obs to UTC time.
    # UTC_OFFSET is a global var.
    df['start'] = df['start'] + timedelta(hours=UTC_OFFSET)
    df['end'] = df['end'] + timedelta(hours=UTC_OFFSET)
    df['start'] = df['start'].dt.tz_localize('UTC')
    df['end'] = df['end'].dt.tz_localize('UTC')

    # Drop NA
    df = df.dropna(subset=value_cols, how='all')

    df = df.set_index('start')
    col_order = (['end', 'TIMESTAMP_START', 'TIMESTAMP_END']
                 + value_cols.to_list())
    df = df[col_order]

    return df

# ---------------------------------------------------------------------------------

def write_df_files(df, text):
    """ 
    Writes a dataframe to a csv file.

    Parameters:
    ----------
    df: dataframe
        Dataframe to write to file.
    text: str
        String to add to output file name.
    Returns:
    -------
    file_path: str
        Path to the file so it can be opened later.
    """

    file_name = "{}_{}.csv".format(analysis, text)
    file_path =os.path.join(csv_path, file_name)
    df.to_csv(path_or_buf=file_path, sep=',', na_rep='NA')

    return(file_path)

# ---------------------------------------------------------------------------------
def read_df_files(file_path):
    """ 
    Reads a csv file of a df back into a df. 
    
    Parameters:
    ----------
    file_path: str
        Path to file to open.
    Returns:
    -------
    df: dataframe
        Dataframe of data.
    """

    #file_name = "{}_{}.csv".format(analysis, text)
    #file_path =os.path.join(csv_path, file_name)

    df = pd.read_csv(file_path)
    df.time = pd.to_datetime(df.time, format='mixed')

    return(df)