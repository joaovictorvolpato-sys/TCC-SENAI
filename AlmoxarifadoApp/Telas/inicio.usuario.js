import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  StatusBar,
  Modal,
  Image,
  Alert,
  RefreshControl,
} from 'react-native';

import { API_URL } from '../config';

const COLUNAS = [
  { chave: 'id', titulo: 'ID', largura: 50 },
  { chave: 'nome', titulo: 'Nome', largura: 140 },
  { chave: 'categoria', titulo: 'Categoria', largura: 120 },
  { chave: 'funcao', titulo: 'Funcao', largura: 140 },
  { chave: 'quantidade', titulo: 'Quantidade', largura: 110 },
  { chave: 'valor', titulo: 'Valor', largura: 90 },
  { chave: 'foto', titulo: 'Foto', largura: 100 },
];

// Monta a URL da foto: aceita "foto.jpg" ou "uploads/foto.jpg"
function urlFoto(foto) {
  const caminho = foto.includes('/') ? foto : 'uploads/' + foto;
  return API_URL + '/static/' + caminho;
}

export default function InicioUsuario({ navigation }) {
  const [itens, setItens] = useState([]);
  const [fotoAberta, setFotoAberta] = useState(null);
  const [atualizando, setAtualizando] = useState(false);

  const carregarItens = useCallback(async () => {
    const controle = new AbortController();
    const limite = setTimeout(() => controle.abort(), 5000);

    try {
      const resposta = await fetch(API_URL + '/api/itens', {
        signal: controle.signal,
      });
      clearTimeout(limite);

      if (!resposta.ok) {
        Alert.alert('Erro', 'Não foi possível carregar o estoque');
        return;
      }
      setItens(await resposta.json());
    } catch (e) {
      clearTimeout(limite);
      console.log('Erro:', e.message);
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    }
  }, []);

  async function puxarParaAtualizar() {
    setAtualizando(true);
    await carregarItens();
    setAtualizando(false);
  }

  // Recarrega sempre que a tela volta a ficar em foco
  useEffect(() => {
    carregarItens();
    const cancelar = navigation.addListener('focus', carregarItens);
    return cancelar;
  }, [navigation, carregarItens]);

  function renderCelula(item, coluna) {
    if (coluna.chave === 'foto') {
      return item.foto ? (
        <TouchableOpacity
          style={styles.botaoFoto}
          onPress={() => setFotoAberta(urlFoto(item.foto))}
        >
          <Text style={styles.botaoTexto}>Foto</Text>
        </TouchableOpacity>
      ) : (
        <Text style={styles.td}>Sem foto</Text>
      );
    }
    return <Text style={styles.td}>{String(item[coluna.chave] ?? '')}</Text>;
  }

  return (
    <View style={styles.corpo}>
      <StatusBar barStyle="light-content" />

      <View style={styles.cabecalho}>
        <Text style={styles.cabecalhoTitulo}>Sistema de Almoxarifado Senai</Text>
        <Text style={styles.cabecalhoSub}>Controle de materiais e estoque</Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={
          <RefreshControl refreshing={atualizando} onRefresh={puxarParaAtualizar} />
        }
      >
        <View style={styles.secaoCards}>
          <View style={styles.card}>
            <Text style={styles.cardTitulo}>Adicionar Estoque</Text>
            <Text style={styles.cardTexto}>Inserir itens ao estoque.</Text>
            <TouchableOpacity
              style={styles.botao}
              onPress={() => navigation.navigate('adicionar')}
            >
              <Text style={styles.botaoTexto}>Acessar</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitulo}>Retirar Estoque</Text>
            <Text style={styles.cardTexto}>Registrar saídas do estoque.</Text>
            <TouchableOpacity
              style={styles.botao}
              onPress={() => navigation.navigate('Retirar')}
            >
              <Text style={styles.botaoTexto}>Acessar</Text>
            </TouchableOpacity>
          </View>
        </View>

        <ScrollView horizontal>
          <View>
            <View style={styles.linhaCabecalho}>
              {COLUNAS.map((c) => (
                <Text key={c.chave} style={[styles.th, { width: c.largura }]}>
                  {c.titulo}
                </Text>
              ))}
            </View>

            {itens.map((item) => (
              <View key={item.id} style={styles.linha}>
                {COLUNAS.map((c) => (
                  <View key={c.chave} style={[styles.celula, { width: c.largura }]}>
                    {renderCelula(item, c)}
                  </View>
                ))}
              </View>
            ))}

            {itens.length === 0 && (
              <Text style={styles.vazio}>Nenhum item no estoque</Text>
            )}
          </View>
        </ScrollView>
      </ScrollView>

      <Modal
        visible={!!fotoAberta}
        transparent
        animationType="fade"
        onRequestClose={() => setFotoAberta(null)}
      >
        <View style={styles.modalFundo}>
          <View style={styles.modalCaixa}>
            {fotoAberta && (
              <Image
                source={{ uri: fotoAberta }}
                style={styles.modalImagem}
                resizeMode="contain"
              />
            )}
            <TouchableOpacity style={styles.botao} onPress={() => setFotoAberta(null)}>
              <Text style={styles.botaoTexto}>Fechar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const AZUL = '#005583';

const styles = StyleSheet.create({
  corpo: { flex: 1, backgroundColor: '#F4F4F4' },
  cabecalho: {
    backgroundColor: AZUL,
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
  },
  cabecalhoTitulo: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  cabecalhoSub: { color: '#FFFFFF', fontSize: 15, marginTop: 6 },
  scroll: { padding: 16, paddingBottom: 40 },
  secaoCards: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  card: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
  },
  cardTitulo: {
    color: AZUL,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  cardTexto: {
    color: '#555555',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 16,
  },
  botao: {
    backgroundColor: AZUL,
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 22,
  },
  botaoTexto: { color: '#FFFFFF', fontSize: 15 },
  linhaCabecalho: { flexDirection: 'row', backgroundColor: AZUL },
  th: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 15,
    paddingVertical: 12,
    paddingHorizontal: 10,
  },
  linha: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDDD',
  },
  celula: { justifyContent: 'center', paddingVertical: 10, paddingHorizontal: 10 },
  td: { color: '#1B2A38', fontSize: 15 },
  botaoFoto: {
    backgroundColor: AZUL,
    borderRadius: 4,
    paddingVertical: 6,
    paddingHorizontal: 12,
    alignSelf: 'flex-start',
  },
  vazio: { padding: 16, color: '#555555', backgroundColor: '#FFFFFF' },
  modalFundo: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  modalCaixa: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
    width: '100%',
    maxWidth: 420,
  },
  modalImagem: { width: '100%', height: 300, marginBottom: 16 },
});