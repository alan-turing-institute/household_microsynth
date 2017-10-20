# utility functions

import numpy as np
import pandas as pd
from random import randint

# econ table sometimes has a slightly lower (1 or 2) count, need to adjust ***at the correct tenure***
def adjust(table, consistent_table):
  for t in table.C_TENHUK11.unique():
    consistent_sum = consistent_table[consistent_table.C_TENHUK11 == t].OBS_VALUE.sum()
    sum = table[table.C_TENHUK11 == t].OBS_VALUE.sum()
    if sum < consistent_sum:
      print("adjusting table tenure", str(t), sum, "->", consistent_sum)
      # randomly increment values (better to scale proportionally)
      r = len(table[table.C_TENHUK11 == t].OBS_VALUE)
      for i in range(sum, consistent_sum):
        index = table[table.C_TENHUK11 == t].OBS_VALUE.index.values
        #print()
        table.OBS_VALUE.at[index[randint(0, r-1)]] += 1
  return table

def unmap(values, mapping):
  """
  Converts values (census category enumerations)
  """
  i = 0
  for m in mapping:
    values.replace(to_replace=m, value=i, inplace=True)
    i += 1

def remap(indices, mapping):
  """
  Converts array of index values back into category values
  """
  values = []
  for i in range(0,len(indices)):
    values.append(mapping[indices[i]])
  return values

def unlistify(table, columns, sizes, values):
  pivot = table.pivot_table(columns=columns, values=values)
  # order must be same as column order above
  a = np.zeros(sizes, dtype=int)
  a[pivot.index.labels] = pivot.values.flat
  return a

def people_per_bedroom(people, bedrooms):
  ppbed = people / bedrooms
  if ppbed <= 0.5:
    return 1 # (0,0.5]
  if ppbed <= 1:
    return 2 # (0.5, 1]
  if ppbed <= 1.5:
    return 3 # (1, 1.5]
  return 4 # >1.5

# make assumption on economic status of residents of different types of communal residence
def communal_economic_status(communal_type):

  # "2": "Medical and care establishment: NHS: Total",
  # "6": "Medical and care establishment: Local Authority: Total",
  # "11": "Medical and care establishment: Registered Social Landlord/Housing Association: Total",
  # "14": "Medical and care establishment: Other: Total",
  # "22": "Other establishment: Defence",
  # "23": "Other establishment: Prison service",
  # "24": "Other establishment: Approved premises (probation/bail hostel)",
  # "25": "Other establishment: Detention centres and other detention",
  # "26": "Other establishment: Education",
  # "27": "Other establishment: Hotel: guest house; B&B; youth hostel",
  # "28": "Other establishment: Hostel or temporary shelter for the homeless",
  # "29": "Other establishment: Holiday accommodation (for example holiday parks)",
  # "30": "Other establishment: Other travel or temporary accommodation",
  # "31": "Other establishment: Religious",
  # "32": "Other establishment: Staff/worker accommodation only",
  # "33": "Other establishment: Other",
  # "34": "Establishment not stated"

  # "4": "Economically active: In employment: Employee: Part-time",
  # "5": "Economically active: In employment: Employee: Full-time",
  # "7": "Economically active: In employment: Self-employed: Part-time",
  # "8": "Economically active: In employment: Self-employed: Full-time",
  # "9": "Economically active: In employment: Full-time students",
  # "11": "Economically active: Unemployed: Unemployed (excluding full-time students)",
  # "12": "Economically active: Unemployed: Full-time students",
  # "14": "Economically inactive: Retired",
  # "15": "Economically inactive: Student (including full-time students)",
  # "16": "Economically inactive: Looking after home or family",
  # "17": "Economically inactive: Long-term sick or disabled",
  # "18": "Economically inactive: Other"

  communal_econ_map = {
    2: -1,
    6: -1,
    11: -1,
    14: -1,
    22: 5,
    23: 18,
    24: 18,
    25: 18,
    26: 9, # or 12?
    27: -1,
    28: 11,
    29: -1,
    30: -1,
    31: 18,
    32: 5,
    33: -1,
    34: -1
  }
  return communal_econ_map[communal_type]

def check(msynth, total_occ_dwellings, total_households, total_communal, total_household_poplb, total_communal_pop):
  # correct number of dwellings
  assert len(msynth.dwellings) == msynth.total_dwellings
  # check no missing/NaN values
  assert not pd.isnull(msynth.dwellings).values.any()

  # category values are within those expected, including unknown/n/a where permitted
  assert np.array_equal(sorted(msynth.dwellings.LC4402_C_TYPACCOM.unique()), np.insert(msynth.type_index, 0, [msynth.NOTAPPLICABLE]))
  assert np.array_equal(sorted(msynth.dwellings.LC4402_C_TENHUK11.unique()), np.insert(msynth.tenure_index, 0, [msynth.NOTAPPLICABLE]))
  assert np.array_equal(sorted(msynth.dwellings.LC4408_C_AHTHUK11.unique()), np.insert(msynth.comp_index, 0, [msynth.UNKNOWN]))
  assert np.array_equal(sorted(msynth.dwellings.LC4408EW_C_PPBROOMHEW11.unique()), msynth.ppb_index)
  assert np.array_equal(sorted(msynth.dwellings.LC4402_C_CENHEATHUK11.unique()), msynth.ch_index)

  # occupied/unoccupied/communal dwelling totals correct
  assert len(msynth.dwellings[(msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)
                            & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)]) == total_occ_dwellings
  assert len(msynth.dwellings[(msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)
                            & (msynth.dwellings.LC4404EW_C_SIZHUK11 == 0)]) == total_households - total_occ_dwellings
  assert len(msynth.dwellings[msynth.dwellings.QS420EW_CELL != msynth.NOTAPPLICABLE]) == total_communal

  # occupied/unoccupied/communal occupants totals correct
  assert msynth.dwellings[(msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)
                            & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)].LC4404EW_C_SIZHUK11.sum() == total_household_poplb
  assert msynth.dwellings[(msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)
                            & (msynth.dwellings.LC4404EW_C_SIZHUK11 == 0)].LC4404EW_C_SIZHUK11.sum() == 0
  assert msynth.dwellings[msynth.dwellings.QS420EW_CELL != msynth.NOTAPPLICABLE].CommunalSize.sum() == total_communal_pop


  # Build (accomodation) type (occupied only)
  for i in msynth.type_index:
    assert len(msynth.dwellings[(msynth.dwellings.LC4402_C_TYPACCOM == i)
                              & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)]) == sum(msynth.lc4402[msynth.lc4402.C_TYPACCOM == i].OBS_VALUE)

  # Tenure (occupied only)
  for i in msynth.tenure_index:
    assert len(msynth.dwellings[(msynth.dwellings.LC4402_C_TENHUK11 == i)
                              & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)]) == sum(msynth.lc4402[msynth.lc4402.C_TENHUK11 == i].OBS_VALUE)

  # central heating (ignoring unoccupied and communal)
  for i in msynth.ch_index:
    assert len(msynth.dwellings[(msynth.dwellings.LC4402_C_CENHEATHUK11 == i)
                              & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                              & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]) == sum(msynth.lc4402[msynth.lc4402.C_CENHEATHUK11 == i].OBS_VALUE)

  # # composition
  for i in msynth.comp_index:
    assert len(msynth.dwellings[(msynth.dwellings.LC4408_C_AHTHUK11 == i)
                             & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                             & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]),  sum(msynth.lc4408[msynth.lc4408.C_AHTHUK11 == i].OBS_VALUE)

  # Rooms (ignoring communal and unoccupied)
  assert np.array_equal(sorted(msynth.dwellings[msynth.dwellings.LC4402_C_TYPACCOM != msynth.NOTAPPLICABLE].LC4404EW_C_ROOMS.unique()), msynth.lc4404["C_ROOMS"].unique())
  for i in msynth.lc4404["C_ROOMS"].unique():
    assert len(msynth.dwellings[(msynth.dwellings.LC4404EW_C_ROOMS == i)
                              & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                              & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]) == sum(msynth.lc4404[msynth.lc4404.C_ROOMS == i].OBS_VALUE)
  # check communal residences rooms are all UNKNOWN
  assert(msynth.dwellings[msynth.dwellings.LC4402_C_TYPACCOM == msynth.NOTAPPLICABLE].LC4404EW_C_ROOMS.unique() == msynth.UNKNOWN)
  # check unoccupied residences rooms are all "known"
  assert(msynth.dwellings[msynth.dwellings.LC4404EW_C_SIZHUK11 == 0].LC4404EW_C_ROOMS.min() > 0)

  # Bedrooms (ignoring communal and unoccupied)
  assert np.array_equal(sorted(msynth.dwellings[msynth.dwellings.LC4402_C_TYPACCOM != msynth.NOTAPPLICABLE].LC4405EW_C_BEDROOMS.unique()), msynth.lc4405["C_BEDROOMS"].unique())
  for i in msynth.lc4405["C_BEDROOMS"].unique():
    assert len(msynth.dwellings[(msynth.dwellings.LC4405EW_C_BEDROOMS == i)
                             & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                             & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]) == sum(msynth.lc4405[msynth.lc4405.C_BEDROOMS == i].OBS_VALUE)
  # check communal residences bedrooms are all UNKNOWN
  assert(msynth.dwellings[msynth.dwellings.LC4402_C_TYPACCOM == msynth.NOTAPPLICABLE].LC4405EW_C_BEDROOMS.unique() == msynth.UNKNOWN)
  # check unoccupied residences bedrooms are all "known"
  assert(msynth.dwellings[msynth.dwellings.LC4404EW_C_SIZHUK11 == 0].LC4405EW_C_BEDROOMS.min() > 0)


  # Economic status (might be small diffs) (ignoring communal and unoccupied)
  assert np.array_equal(sorted(msynth.dwellings[msynth.dwellings.LC4601EW_C_ECOPUK11 != msynth.UNKNOWN].LC4601EW_C_ECOPUK11.unique()), msynth.lc4601["C_ECOPUK11"].unique())
  for i in msynth.lc4601["C_ECOPUK11"].unique():
    assert len(msynth.dwellings[(msynth.dwellings.LC4601EW_C_ECOPUK11 == i)
                             & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                             & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]) >= sum(msynth.lc4601[msynth.lc4601["C_ECOPUK11"] == i].OBS_VALUE)

  # Ethnicity (ignoring communal and unoccupied)
  assert np.array_equal(sorted(msynth.dwellings[msynth.dwellings.LC4202EW_C_ETHHUK11 != msynth.UNKNOWN].LC4202EW_C_ETHHUK11.unique()), msynth.lc4202["C_ETHHUK11"].unique())
  for i in msynth.lc4202["C_ETHHUK11"].unique():
    assert len(msynth.dwellings[(msynth.dwellings.LC4202EW_C_ETHHUK11 == i)
                             & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                             & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]) == sum(msynth.lc4202[msynth.lc4202["C_ETHHUK11"] == i].OBS_VALUE)

 # Cars (ignoring communal and unoccupied)
  assert np.array_equal(sorted(msynth.dwellings[msynth.dwellings.LC4202EW_C_CARSNO != msynth.UNKNOWN].LC4202EW_C_CARSNO.unique()), msynth.lc4202["C_CARSNO"].unique())
  for i in msynth.lc4202["C_CARSNO"].unique():
    assert len(msynth.dwellings[(msynth.dwellings.LC4202EW_C_CARSNO == i)
                             & (msynth.dwellings.LC4404EW_C_SIZHUK11 != 0)
                             & (msynth.dwellings.QS420EW_CELL == msynth.NOTAPPLICABLE)]) == sum(msynth.lc4202[msynth.lc4202["C_CARSNO"] == i].OBS_VALUE)

  return True


