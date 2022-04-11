import math
import pickle
import datetime
import inflection
import numpy as np
import pandas as pd

class Rossmann( object ):

    def __init__( self ):
        self.home_path = '/home/alex/repos/repos/projeto_DS_producao/'
        self.competition_distance_scaler   = pickle.load( open( self.home_path + 'parameter/competition_distance_scaler.pkl', 'rb'))
        self.competition_distance_scaler   = pickle.load( open( self.home_path + 'parameter/competition_distance_scaler.pkl', 'rb'))
        self.year_scaler                   = pickle.load( open( self.home_path + 'parameter/year_scaler.pkl', 'rb'))
        self.competition_time_month_scaler = pickle.load( open( self.home_path + 'parameter/competition_time_month_scaler.pkl', 'rb'))
        self.promo_time_week_scaler        = pickle.load( open( self.home_path + 'parameter/promo_time_week_scaler.pkl', 'rb'))
        self.store_type_scaler             = pickle.load( open( self.home_path + 'parameter/store_type_scaler.pkl', 'rb'))


    def data_cleaning( self, df1):

        #1.1 Rename Columns
        cols_old = ['Store', 'DayOfWeek', 'Date', 'Open', 'Promo',
            'StateHoliday', 'SchoolHoliday', 'StoreType', 'Assortment',
            'CompetitionDistance', 'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear',
            'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']

        snakecase = lambda x: inflection.underscore( x )

        cols_new = list(map( snakecase, cols_old))

        # rename
        df1.columns = cols_new

        #1.3 Data Types
        df1['date'] = pd.to_datetime( df1['date'])

        #1.5 Fillout NA
        # competition_distance
        df1['competition_distance'] = df1['competition_distance'].apply( lambda x: 200000.0 if math.isnan( x ) else x)

        # competition_open_since_month
        df1['competition_open_since_month'] = df1.apply( lambda x: x['date'].month if math.isnan( x['competition_open_since_month'] ) else x['competition_open_since_month'], axis=1)

        # competition_open_since_year
        df1['competition_open_since_year'] = df1.apply( lambda x: x['date'].year if math.isnan( x['competition_open_since_year'] ) else x['competition_open_since_year'], axis=1)

        # promo2_since_week
        df1['promo2_since_week'] = df1.apply( lambda x: x['date'].week if math.isnan( x['promo2_since_week'] ) else x['promo2_since_week'], axis=1)

        # promo2_since_year
        df1['promo2_since_year'] = df1.apply( lambda x: x['date'].year if math.isnan( x['promo2_since_year'] ) else x['promo2_since_year'], axis=1)

        # promo_interval
        month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec' }

        df1['promo_interval'].fillna(0, inplace=True)

        df1['month_map'] = df1['date'].dt.month.map( month_map )

        df1['is_promo'] = df1[['promo_interval', 'month_map']].apply( lambda x: 0 if x['promo_interval'] == 0 else 1 if x['month_map'] in x['promo_interval'].split( ',' ) else 0, axis=1 )

        #1.6 Change Types
        # competition
        df1['competition_open_since_month'] = df1['competition_open_since_month'].astype( int )
        df1['competition_open_since_year'] = df1['competition_open_since_year'].astype( int )

        # promo 2
        df1['promo2_since_week'] = df1['promo2_since_week'].astype( int )
        df1['promo2_since_year'] = df1['promo2_since_year'].astype( int )

        return df1


    def feature_engineering( self, df2):

        # year
        df2['year'] = df2['date'].dt.year

        #month
        df2['month'] = df2['date'].dt.month

        #day
        df2['day'] = df2['date'].dt.day

        #week of year
        df2['week_of_year'] = df2['date'].dt.weekofyear

        #year week
        df2['year_week'] = df2['date'].dt.strftime( '%Y-%W' )

        #competition since
        df2['competition_since'] = df2.apply(lambda x: datetime.datetime( year=x['competition_open_since_year'], month=x['competition_open_since_month'], day=1), axis=1)
        df2['competition_since_month'] = ((df2['date'] - df2['competition_since'])/30).apply(lambda x: x.days).astype( int )
        df2['competition_time_month'] = ((df2['date'] - df2['competition_since'])/30).apply(lambda x: x.days).astype( int )

        #promo since
        df2['promo_since'] = df2['promo2_since_year'].astype(str) + '-' + df2['promo2_since_week'].astype(str)
        df2['promo_since'] = df2['promo_since'].apply(lambda x: datetime.datetime.strptime( x + '-1', '%Y-%W-%w' ) - datetime.timedelta( days=7 ))
        df2['promo_time_week'] = ( ( df2['date'] - df2['promo_since'] )/7 ).apply(lambda x: x.days ).astype( int )

        #assortment / a=basic, b=extra, c=extended
        df2['assortment'] = df2['assortment'].apply(lambda x: 'basic' if x == 'a' else 'extra' if x == 'b' else 'extended')

        #state holiday / a=public holiday, b=easter holiday, c=christmas
        df2['state_holiday'] = df2['state_holiday'].apply(lambda x: 'public_holiday' if x == 'a' else 'easter_holiday' if x == 'b' else 'christmas' if x =='c' else 'regular_day')

        #3.0 Filtragem de Variáveis
        #3.1 Filtragem das Linhas
        df2 = df2[(df2['open'] != 0)]

        #3.2 Seleção das Colunas
        df2 = df2.drop( columns = ['open', 'promo_interval', 'month_map'] )

        return df2


    def data_preparation( self, df4 ):

        #5.2 Rescaling
        # competition distance
        df4['competition_distance'] = self.competition_distance_scaler.transform(df4[['competition_distance']].values)

        # year
        df4['year'] = self.year_scaler.transform(df4[['year']].values)

        # competition time month
        df4['competition_time_month'] = self.competition_time_month_scaler.transform(df4[['competition_time_month']].values)

        #promo time week
        df4['promo_time_week'] = self.promo_time_week_scaler.transform(df4[['promo_time_week']].values)

        #5.3.1 Encoding
        #state_holiday - onehot encoding
        df4 = pd.get_dummies( df4, prefix=['state_holiday'], columns=['state_holiday'])

        #store_type - label encoding
        df4['store_type'] = self.store_type_scaler.transform(df4['store_type'])

        #assortment - ordinal encoding
        assortment_dict = {'basic': 1, 'extra': 2, 'extended': 3}
        df4['assortment'] = df4['assortment'].map( assortment_dict )

        #5.3.3 Nature Transformation
        # day
        df4['day_sin'] = df4['day'].apply( lambda x: np.sin( x * (2 * np.pi/30)))
        df4['day_cos'] = df4['day'].apply( lambda x: np.cos( x * (2 * np.pi/30)))

        # day of week
        df4['day_of_week_sin'] = df4['day_of_week'].apply( lambda x: np.sin( x * (2 * np.pi/7)))
        df4['day_of_week_cos'] = df4['day_of_week'].apply( lambda x: np.cos( x * (2 * np.pi/7)))

        # month
        df4['month_sin'] = df4['month'].apply( lambda x: np.sin( x * (2 * np.pi/12)))
        df4['month_cos'] = df4['month'].apply( lambda x: np.cos( x * (2 * np.pi/12)))

        # week of year
        df4['week_of_year_sin'] = df4['week_of_year'].apply( lambda x: np.sin( x * (2 * np.pi/52)))
        df4['week_of_year_cos'] = df4['week_of_year'].apply( lambda x: np.cos( x * (2 * np.pi/52)))

        cols_selected = [ 'store', 'promo', 'store_type', 'assortment', 'competition_distance',
                                'competition_open_since_month', 'competition_open_since_year', 'promo2',
                                'promo2_since_week', 'promo2_since_year', 'competition_since_month',
                                'competition_time_month', 'promo_time_week', 'day_sin', 'day_cos',
                                'day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos',
                                'week_of_year_sin', 'week_of_year_cos']

        df4 = df4[ cols_selected ]

        return df4

    def get_prediction( self, model, original_data, test_data):
        # prediction
        pred = model.predict( test_data )

        # join pred into the original data
        original_data['prediction'] = np.expm1( pred )

        return original_data.to_json( orient='records', date_format='iso')
