import * as api from '../api'
import * as types from './mutations-types'

export default {
    getAllFlats ({ commit }) {
        commit(types.IS_LOADING)
        api.getFlats(flats => {
            commit(types.REPLACE_FLATS, { flats })
        })
    },
    getFlat ({ commit }, { flatId }) {
        commit(types.IS_LOADING)
        api.getFlat(flatId, flat => {
            const flats = [flat]
            commit(types.MERGE_FLATS, { flats })
        })
    },
    getAllTimeToPlaces ({ commit }) {
        commit(types.IS_LOADING)
        api.getTimeToPlaces(timeToPlaces => {
            commit(types.RECEIVE_TIME_TO_PLACES, { timeToPlaces })
        })
    },
    updateFlatStatus ({ commit }, { flatId, newStatus }) {
        commit(types.IS_LOADING)
        api.updateFlatStatus(flatId, newStatus, response => {
            commit(types.UPDATE_FLAT_STATUS, { flatId, newStatus })
        })
    },
    updateFlatNotes ({ commit }, { flatId, newNotes }) {
        commit(types.IS_LOADING)
        api.updateFlatNotes(flatId, newNotes, response => {
            commit(types.UPDATE_FLAT_NOTES, { flatId, newNotes })
        })
    },
    doSearch ({ commit }, { query }) {
        commit(types.IS_LOADING)
        api.doSearch(query, flats => {
            commit(types.REPLACE_FLATS, { flats })
        })
    }
}
